import sys
import io
import time
import json
import requests
import threading
import traceback
import collections
import warnings

try:
    import Queue as queue
except ImportError:
    import queue

# Suppress InsecurePlatformWarning
requests.packages.urllib3.disable_warnings()


_classmap = {}

# Function to produce namedtuple classes.
def _create_class(typename, fields):    
    # extract field names
    field_names = [e[0] if type(e) is tuple else e for e in fields]

    # extract (non-simple) fields that need conversions
    conversions = list(filter(lambda e: type(e) is tuple, fields))

    # Some dictionary keys are Python keywords and cannot be used as field names, e.g. `from`.
    # Get around by appending a '_', e.g. dict['from'] => namedtuple.from_
    keymap = [(k.rstrip('_'), k) for k in filter(lambda e: e in ['from_'], field_names)]

    # Create the base tuple class, with defaults.
    base = collections.namedtuple(typename, field_names)
    base.__new__.__defaults__ = (None,) * len(field_names)

    class sub(base):
        def __new__(cls, **kwargs):
            # Map keys.
            for oldkey, newkey in keymap:
                kwargs[newkey] = kwargs[oldkey]
                del kwargs[oldkey]

            # Any unexpected arguments?
            unexpected = set(kwargs.keys()) - set(super(sub, cls)._fields)

            # Remove unexpected arguments and issue warning.
            if unexpected:
                for k in unexpected:
                    del kwargs[k]

                s = ('Unexpected fields: ' + ', '.join(unexpected) + ''
                     '\nBot API seems to have added new fields to the returned data.'
                     ' This version of namedtuple is not able to capture them.'
                     '\n\nPlease upgrade telepot by:'
                     '\n  sudo pip install telepot --upgrade'
                     '\n\nIf you still see this message after upgrade, that means I am still working to bring the code up-to-date.'
                     ' Please try upgrade again a few days later.'
                     ' In the meantime, you can access the new fields the old-fashioned way, through the raw dictionary.')

                warnings.warn(s, UserWarning)

            # Convert non-simple values to namedtuples.
            for key, func in conversions:
                if key in kwargs:
                    if type(kwargs[key]) is dict:
                        kwargs[key] = func(**kwargs[key])
                    elif type(kwargs[key]) is list:
                        kwargs[key] = func(kwargs[key])
                    else:
                        raise RuntimeError('Can only convert dict or list')

            return super(sub, cls).__new__(cls, **kwargs)

    sub.__name__ = typename
    _classmap[typename] = sub

    return sub


User = _create_class('User', ['id', 'first_name', 'last_name', 'username'])
Chat = _create_class('Chat', ['id', 'type', 'title', 'username', 'first_name', 'last_name'])
PhotoSize = _create_class('PhotoSize', ['file_id', 'width', 'height', 'file_size'])

Audio = _create_class('Audio', ['file_id', 'duration', 'performer', 'title', 'mime_type', 'file_size'])
Document = _create_class('Document', ['file_id', ('thumb', PhotoSize), 'file_name', 'mime_type', 'file_size'])
Sticker = _create_class('Sticker', ['file_id', 'width', 'height', ('thumb', PhotoSize), 'file_size'])
Video = _create_class('Video', ['file_id', 'width', 'height', 'duration', ('thumb', PhotoSize), 'mime_type', 'file_size'])
Voice = _create_class('Voice', ['file_id', 'duration', 'mime_type', 'file_size'])

Contact = _create_class('Contact', ['phone_number', 'first_name', 'last_name', 'user_id'])
Location = _create_class('Location', ['longitude', 'latitude'])
File = _create_class('File', ['file_id', 'file_size', 'file_path'])

def PhotoSizeArray(data):
    return [PhotoSize(**p) for p in data]

_classmap['PhotoSize[]'] = PhotoSizeArray

def PhotoSizeArrayArray(data):
    return [[PhotoSize(**p) for p in array] for array in data]

_classmap['PhotoSize[][]'] = PhotoSizeArrayArray

UserProfilePhotos = _create_class('UserProfilePhotos', ['total_count', ('photos', PhotoSizeArrayArray)])

Message = _create_class('Message', [
              'message_id',
              ('from_', User),
              'date',
              ('chat', Chat),
              ('forward_from', User),
              'forward_date',
              ('reply_to_message', lambda **kwargs: _classmap['Message'](**kwargs)),  # get around the fact that `Message` is not yet defined
              'text',
              ('audio', Audio),
              ('document', Document),
              ('photo', PhotoSizeArray),
              ('sticker', Sticker),
              ('video', Video),
              ('voice', Voice),
              'caption',
              ('contact', Contact),
              ('location', Location),
              ('new_chat_participant', User),
              ('left_chat_participant', User),
              'new_chat_title',
              ('new_chat_photo', PhotoSizeArray),
              'delete_chat_photo',
              'group_chat_created',
              'supergroup_chat_created', 
              'channel_chat_created', 
              'migrate_to_chat_id', 
              'migrate_from_chat_id',
          ])

Update = _create_class('Update', ['update_id', ('message', Message)])

def UpdateArray(data):
    return [Update(**u) for u in data]

_classmap['Update[]'] = UpdateArray


"""
Convert a dictionary to a namedtuple, given the type of object.
You can see what `type` is valid by entering this in Python interpreter:
>>> import telepot
>>> print telepot._classmap
It includes all Bot API objects you may get back from the server, plus a few.
"""
def namedtuple(data, type):
    if type[-2:] == '[]':
        return _classmap[type](data)
    else:
        return _classmap[type](**data)


def _infer_content_type(msg):
    types = [
        'text', 'voice', 'sticker', 'photo', 'audio' ,'document', 'video', 'contact', 'location',
        'new_chat_participant', 'left_chat_participant',  'new_chat_title', 'new_chat_photo',  'delete_chat_photo', 'group_chat_created', 
        'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id',
    ]

    content_type = list(filter(lambda f: f in msg, types))

    if len(content_type) > 1:
        raise RuntimeError('Inferred multiple content types from message', msg)
    elif len(content_type) < 1:
        raise RuntimeError('Cannot infer content type from message', msg)

    return content_type[0]


def glance(msg, long=False):
    content_type = _infer_content_type(msg)

    if long:
        return content_type, msg['from']['id'], msg['chat']['id'], msg['date'], msg['message_id']
    else:
        return content_type, msg['from']['id'], msg['chat']['id']


def glance2(msg, long=False):
    content_type = _infer_content_type(msg)

    if long:
        return content_type, msg['chat']['type'], msg['chat']['id'], msg['date'], msg['message_id']
    else:
        return content_type, msg['chat']['type'], msg['chat']['id']


class TelepotException(Exception):
    pass

class BadHTTPResponse(TelepotException):
    def __init__(self, status, text):
        super(BadHTTPResponse, self).__init__(status, text)

    @property
    def status(self):
        return self.args[0]

    @property
    def text(self):
        return self.args[1]

class TelegramError(TelepotException):
    def __init__(self, description, error_code):
        super(TelegramError, self).__init__(description, error_code)

    @property
    def description(self):
        return self.args[0]

    @property
    def error_code(self):
        return self.args[1]


class Bot(object):
    def __init__(self, token):
        self._token = token
        self._msg_thread = None

        # Ensure an exception is raised for requests that take too long
        self._http_timeout = 30

        # For streaming file download
        self._file_chunk_size = 65536

    def _fileurl(self, path):
        return 'https://api.telegram.org/file/bot%s/%s' % (self._token, path)

    def _methodurl(self, method):
        return 'https://api.telegram.org/bot%s/%s' % (self._token, method)

    def _parse(self, response):
        try:
            data = response.json()
        except ValueError:  # No JSON object could be decoded
            raise BadHTTPResponse(response.status_code, response.text)

        if data['ok']:
            return data['result']
        else:
            raise TelegramError(data['description'], data['error_code'])

    def _rectify(self, params):
        # remove None, then json-serialize if needed
        return {key: value if type(value) not in [dict, list] else json.dumps(value, separators=(',',':')) for key,value in params.items() if value is not None}

    def getMe(self):
        r = requests.post(self._methodurl('getMe'), timeout=self._http_timeout)
        return self._parse(r)

    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode, 'disable_web_page_preview': disable_web_page_preview, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._methodurl('sendMessage'), params=self._rectify(p), timeout=self._http_timeout)
        return self._parse(r)

    def forwardMessage(self, chat_id, from_chat_id, message_id):
        p = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}
        r = requests.post(self._methodurl('forwardMessage'), params=self._rectify(p), timeout=self._http_timeout)
        return self._parse(r)

    def _isfile(self, f):
        if sys.version_info.major >= 3:
            return isinstance(f, io.IOBase)
        else:
            return type(f) is file

    def _sendFile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if self._isfile(inputfile):
            files = {filetype: inputfile}
            r = requests.post(self._methodurl(method), params=self._rectify(params), files=files)

            # `self._http_timeout` is not used here because, for some reason, the larger the file, 
            # the longer it takes for the server to respond (after upload is finished). It is hard to say
            # what value `self._http_timeout` should be. In the future, maybe I should let user specify.
        else:
            params[filetype] = inputfile
            r = requests.post(self._methodurl(method), params=self._rectify(params), timeout=self._http_timeout)

        return self._parse(r)

    def sendPhoto(self, chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(photo, 'photo', {'chat_id': chat_id, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendAudio(self, chat_id, audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(audio, 'audio', {'chat_id': chat_id, 'duration': duration, 'performer': performer, 'title': title, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendDocument(self, chat_id, document, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(document, 'document', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendSticker(self, chat_id, sticker, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(sticker, 'sticker', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendVideo(self, chat_id, video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(video, 'video', {'chat_id': chat_id, 'duration': duration, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendVoice(self, chat_id, audio, duration=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(audio, 'voice', {'chat_id': chat_id, 'duration': duration, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendLocation(self, chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._methodurl('sendLocation'), params=self._rectify(p), timeout=self._http_timeout)
        return self._parse(r)

    def sendChatAction(self, chat_id, action):
        p = {'chat_id': chat_id, 'action': action}
        r = requests.post(self._methodurl('sendChatAction'), params=self._rectify(p), timeout=self._http_timeout)
        return self._parse(r)

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = {'user_id': user_id, 'offset': offset, 'limit': limit}
        r = requests.post(self._methodurl('getUserProfilePhotos'), params=self._rectify(p), timeout=self._http_timeout)
        return self._parse(r)

    def getFile(self, file_id):
        p = {'file_id': file_id}
        r = requests.post(self._methodurl('getFile'), params=self._rectify(p), timeout=self._http_timeout)
        return self._parse(r)

    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = {'offset': offset, 'limit': limit, 'timeout': timeout}
        r = requests.post(self._methodurl('getUpdates'), params=self._rectify(p), timeout=self._http_timeout+(0 if timeout is None else timeout))
        return self._parse(r)

    def setWebhook(self, url=None, certificate=None):
        p = {'url': url}

        if certificate:
            files = {'certificate': certificate}
            r = requests.post(self._methodurl('setWebhook'), params=self._rectify(p), files=files, timeout=self._http_timeout)
        else:
            r = requests.post(self._methodurl('setWebhook'), params=self._rectify(p), timeout=self._http_timeout)

        return self._parse(r)

    def downloadFile(self, file_id, dest):
        f = self.getFile(file_id)

        # `file_path` is optional in File object
        if 'file_path' not in f:
            raise TelegramError('No file_path returned', None)

        try:
            r = requests.get(self._fileurl(f['file_path']), stream=True, timeout=self._http_timeout)

            d = dest if self._isfile(dest) else open(dest, 'wb')

            for chunk in r.iter_content(chunk_size=self._file_chunk_size):
                if chunk:
                    d.write(chunk)
                    d.flush()
        finally:
            if not self._isfile(dest) and 'd' in locals():
                d.close()

            if 'r' in locals():
                r.close()

    def notifyOnMessage(self, callback=None, relax=0.1, timeout=20, source=None, ordered=True, maxhold=3, run_forever=False):
        if callback is None:
            callback = self.handle

        def handle(update):
            try:
                callback(update['message'])
            except:
                # Localize the error so message thread can keep going.
                traceback.print_exc()
            finally:
                return update['update_id']

        def get_from_telegram_server():
            offset = None  # running offset
            while 1:
                try:
                    result = self.getUpdates(offset=offset, timeout=timeout)

                    if len(result) > 0:
                        # No sort. Trust server to give messages in correct order.
                        # Update offset to max(update_id) + 1
                        offset = max([handle(update) for update in result]) + 1
                except:
                    traceback.print_exc()
                finally:
                    time.sleep(relax)

        def dictify3(data):
            if type(data) is bytes:
                return json.loads(data.decode('utf-8'))
            elif type(data) is str:
                return json.loads(data)
            elif type(data) is dict:
                return data
            else:
                raise ValueError()

        def dictify27(data):
            if type(data) in [str, unicode]:
                return json.loads(data)
            elif type(data) is dict:
                return data
            else:
                raise ValueError()

        def get_from_queue_unordered(qu):
            dictify = dictify3 if sys.version_info >= (3,) else dictify27
            while 1:
                try:
                    data = qu.get(block=True)
                    update = dictify(data)
                    handle(update)
                except:
                    traceback.print_exc()

        def get_from_queue(qu):
            dictify = dictify3 if sys.version_info >= (3,) else dictify27

            # Here is the re-ordering mechanism, ensuring in-order delivery of updates.
            max_id = None                 # max update_id passed to callback
            buffer = collections.deque()  # keep those updates which skip some update_id
            qwait = None                  # how long to wait for updates,
                                          # because buffer's content has to be returned in time.

            while 1:
                try:
                    data = qu.get(block=True, timeout=qwait)
                    update = dictify(data)

                    if max_id is None:
                        # First message received, handle regardless.
                        max_id = handle(update)

                    elif update['update_id'] == max_id + 1:
                        # No update_id skipped, handle naturally.
                        max_id = handle(update)

                        # clear contagious updates in buffer
                        if len(buffer) > 0:
                            buffer.popleft()  # first element belongs to update just received, useless now.
                            while 1:
                                try:
                                    if type(buffer[0]) is dict:
                                        max_id = handle(buffer.popleft())  # updates that arrived earlier, handle them.
                                    else:
                                        break  # gap, no more contagious updates
                                except IndexError:
                                    break  # buffer empty

                    elif update['update_id'] > max_id + 1:
                        # Update arrives pre-maturely, insert to buffer.
                        nbuf = len(buffer)
                        if update['update_id'] <= max_id + nbuf:
                            # buffer long enough, put update at position
                            buffer[update['update_id'] - max_id - 1] = update
                        else:
                            # buffer too short, lengthen it
                            expire = time.time() + maxhold
                            for a in range(nbuf, update['update_id']-max_id-1):
                                buffer.append(expire)  # put expiry time in gaps
                            buffer.append(update)

                    else:
                        pass  # discard

                except queue.Empty:
                    # debug message
                    # print('Timeout')

                    # some buffer contents have to be handled
                    # flush buffer until a non-expired time is encountered
                    while 1:
                        try:
                            if type(buffer[0]) is dict:
                                max_id = handle(buffer.popleft())
                            else:
                                expire = buffer[0]
                                if expire <= time.time():
                                    max_id += 1
                                    buffer.popleft()
                                else:
                                    break  # non-expired
                        except IndexError:
                            break  # buffer empty
                except:
                    traceback.print_exc()
                finally:
                    try:
                        # don't wait longer than next expiry time
                        qwait = buffer[0] - time.time()
                        if qwait < 0:
                            qwait = 0
                    except IndexError:
                        # buffer empty, can wait forever
                        qwait = None

                    # debug message
                    # print ('Buffer:', str(buffer), ', To Wait:', qwait, ', Max ID:', max_id)

        if source is None:
            t = threading.Thread(target=get_from_telegram_server)
        elif isinstance(source, queue.Queue):
            if ordered:
                t = threading.Thread(target=get_from_queue, args=(source,))
            else:
                t = threading.Thread(target=get_from_queue_unordered, args=(source,))
        else:
            raise ValueError('Invalid source')

        t.daemon = True  # need this for main thread to be killable by Ctrl-C
        t.start()

        if run_forever:
            while 1:
                time.sleep(10)


import inspect
import telepot.helper


class SpeakerBot(Bot):
    def __init__(self, token):
        super(SpeakerBot, self).__init__(token)
        self._mic = telepot.helper.Microphone()

    @property
    def mic(self):
        return self._mic

    def create_listener(self):
        q = queue.Queue()
        self._mic.add(q)
        ln = telepot.helper.Listener(self._mic, q)
        return ln


class DelegatorBot(SpeakerBot):
    def __init__(self, token, delegation_patterns):
        super(DelegatorBot, self).__init__(token)
        self._delegate_records = [p+({},) for p in delegation_patterns]

    def _startable(self, delegate):
        return ((hasattr(delegate, 'start') and inspect.ismethod(delegate.start)) and
                (hasattr(delegate, 'is_alive') and inspect.ismethod(delegate.is_alive)))

    def _tuple_is_valid(self, t):
        return len(t) == 3 and callable(t[0]) and type(t[1]) in [list, tuple] and type(t[2]) is dict

    def _ensure_startable(self, delegate):
        if self._startable(delegate):
            return delegate
        elif callable(delegate):
            return threading.Thread(target=delegate)
        elif type(delegate) is tuple and self._tuple_is_valid(delegate):
            func, args, kwargs = delegate
            return threading.Thread(target=func, args=args, kwargs=kwargs)
        else:
            raise RuntimeError('Delegate does not have the required methods, is not callable, and is not a valid tuple.')

    def handle(self, msg):
        self._mic.send(msg)

        for calculate_seed, make_delegate, dict in self._delegate_records:
            id = calculate_seed(msg)
            
            if id is None:
                continue
            elif isinstance(id, collections.Hashable):
                if id not in dict or not dict[id].is_alive():
                    d = make_delegate((self, msg, id))
                    d = self._ensure_startable(d)

                    dict[id] = d
                    dict[id].start()
            else:
                d = make_delegate((self, msg, id))
                d = self._ensure_startable(d)
                d.start()
