import os
import json
import logging
from logging import FileHandler, Formatter
from .config import Config
from .nicovideo_api import *
from .sound_extractor import SoundExtractorFactory
from .exception import *

class Gazeru:
    def __init__(self):
        self.config = Config()
        self.niconico = NicovideoAPI(self.config.get_user(), self.config.get_password())
        self.sound_extractor_factory = SoundExtractorFactory()
        self.dot_gazeru = '{0}/.gazeru'.format(self.config.get_directory())
        self.GAZEL_HOME = '{0}/.gazeru'.format(os.environ['HOME'])
        self.setup_logger()

    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s- %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        file_handler = FileHandler('{0}/log/gazeru.log'.format(self.GAZEL_HOME), 'a+')
        file_handler.level = logging.INFO
        file_handler.formatter = Formatter(fmt='%(asctime)s %(message)s', datefmt='%Y/%m/%d %p %I:%M:%S')
        self.logger.addHandler(file_handler)
        return self

    def get_mylists(self):
        return self.config.get_mylists()

    def set_account(self, user, password):
        self.config.set_user(user)
        self.config.set_password(password)
        self.niconico.login(self.config.get_user(), self.config.get_password())
        self.logger.info('set user and password')
        return self

    def set_directory(self, directory):
        self.config.set_directory(directory)
        self.dot_gazeru = '{0}/.gazeru'.format(self.config.get_directory())
        self.logger.info('set directory to {0}'.format(directory))
        return self

    def add_mylist(self, mylist_id):
        registered_mylist_id_list = [mylist['id'] for mylist in self.config.get_mylists().values()]
        if mylist_id in registered_mylist_id_list:
            raise AlreadyRegisteredMylistError()
        try:
            mylist_info = self.niconico.get_mylist_info(mylist_id)
        except NotFoundError:
            raise NotFoundMylistError()
        self.config.add_mylist({mylist_info['id']: {'id': mylist_info['id'], 'creator': mylist_info['creator'], 'title': mylist_info['title']}})
        self.logger.info('add mylist {0}'.format(mylist_id))

    def remove_mylist(self, mylist_id):
        registered_mylist_id_list = [mylist['id'] for mylist in self.config.get_mylists().values()]
        if mylist_id not in registered_mylist_id_list:
            raise NotRegisteredMylistError()
        self.config.remove_mylist(mylist_id)
        self.logger.info('remove mylist {0}'.format(mylist_id))

    def get_uploaded(self):
        uploaded = {mylist['id']: self.niconico.get_mylist_info(mylist['id'])['video_list'] for mylist in self.config.get_mylists().values()}
        return uploaded

    def get_logged(self):
        with open(self.dot_gazeru, 'r') as file:
            downloaded = json.loads(file.read())
        return downloaded

    def get_existed_creator_mylists(self, creator):
        return os.listdir('{0}/{1}'.format(self.config.get_directory(), creator))

    def get_existed_creator_mylist_songs(self, creator, mylist):
        return os.listdir('{0}/{1}/{2}'.format(self.config.get_directory(), creator, mylist))

    def get_existed(self):
        """
        {'164': {'マイリス': [], 'mylis2': []}, 'sasakureUK': {'マイリス': []}}
        """
        creators = os.listdir(self.config.get_directory())
        creators.remove('.gazeru')
        existed = {creator:
                   {mylist:
                    [self.get_existed_creator_mylist_songs(creator, mylist)]
                    for mylist in self.get_existed_creator_mylists(creator)}
                   for creator in creators}
        return existed

    def get_downloaded(self):
        existed = self.get_existed()
        # {'164': {'マイリス': [], 'mylis2': []}, 'sasakureUK': {'マイリス': []}}
        logged = self.get_logged()
        # {'sasakureUK': {'mylist': {'id': 12313, 'video_list': {'hogehoge': 'sm12312'}}}}
        # {mylist_id: [video_id, video_id], mylist_id2: []}
        downloaded = {}
        for creator, mylists in existed.items():
            for mylist_title, songs in mylists.items():
                if creator in logged and mylist_title in logged[creator]:
                    downloaded.update({logged[creator][mylist_title]['id']: [video_id for video_title, video_id in logged[creator][mylist_title]['video_list'].items() if video_title in songs]})
        return downloaded

    def pull(self):
        if not os.path.exists(self.dot_gazeru):
            self.create_dot_gazeru()
            self.logger.info('create {0}'.format(self.dot_gazeru))
        mylist_infos = {mylist['id']: self.niconico.get_mylist_info(mylist['id']) for mylist in self.config.get_mylists().values()}
        downloaded = self.get_downloaded()
        uploaded = {mylist_info['id']: mylist_info['video_list'] for mylist_id, mylist_info in mylist_infos.items()}
        downloading = {mylist_id:
                       [video_id
                        for video_id in video_list
                        if mylist_id not in downloaded.keys()
                        or video_id not in downloaded[mylist_id]]
                       for mylist_id, video_list in uploaded.items()}
        self.logger.info('downloading {0}'.format(downloading))
        for mylist_id,video_id_list in downloading.items():
            for video_id in video_id_list:
                try:
                    video, video_info = self.download_video(video_id)
                    sound,sound_type = self.extract_sound(video, video_info)
                    sound_file_path = '{0}/{1}/{2}'.format(self.config.get_directory(), mylist_infos[mylist_id]['creator'], mylist_infos[mylist_id]['title'])
                    os.makedirs(sound_file_path, exist_ok=True)
                    sound_file = '{0}.{1}'.format(self.escape_slash(video_info['title']), sound_type)
                    full_sound_file_path = '{0}/{1}'.format(sound_file_path, sound_file)
                    self.logger.info('start writing {0} to {1}'.format(video_id, full_sound_file_path))
                    with open(full_sound_file_path, 'wb') as file:
                        file.write(sound)
                    self.logger.info('finished writing {0} to {1}'.format(video_id, full_sound_file_path))
                    self.logger.info('start updating .gazeru')
                    self.update_dot_gazeru(mylist_infos, video_info)
                    self.logger.info('finished updating .gazeru')
                except Exception as e:
                    self.logger.critical(e.value)
                    self.logger.error('{0} is not downloaded'.format(video_id))

    def escape_slash(self, title):
        return title.replace("/", "／")

    def extract_sound(self, video, video_info):
        self.logger.info('start exstacting {0}'.format(video_info['video_id']))
        sound_extractor = self.sound_extractor_factory.build(video, video_info['movie_type'])
        result = (sound_extractor.extract(video), sound_extractor.get_sound_type())
        self.logger.info('finished exstracting {0}'.format(video_info['video_id']))
        return result

    def download_video(self, video_id):
        self.logger.info('start downloading {0}'.format(video_id))
        result = (self.niconico.get_flv(video_id), self.niconico.get_thumb_info(video_id))
        self.logger.info('finished downloading {0}'.format(video_id))
        return result

    def create_dot_gazeru(self):
        """
        {'sasakureUK': {'mylist': {'id': 12313, 'video_list': {'hogehoge': 'sm12312'}}}}
        """
        dot_gazeru = {mylist['creator']:
                      {mylist['title']:
                       {'id': mylist['id'], 'video_list': {}}
                      }
                      for mylist in self.config.get_mylists().values()}
        with open(self.dot_gazeru, 'w') as file:
            file.write(json.dumps(dot_gazeru))
        return self

    def update_dot_gazeru(self, mylist_infos, video_info):
        dot_gazeru = {mylist['creator']:
                      {mylist['title']:
                      {'id': mylist['id'],
                       'video_list': {video_info['title']: video_id for video_id in mylist_infos[mylist['id']]['video_list']}}
                      }
                      for mylist in self.config.get_mylists().values()}
        with open(self.dot_gazeru, 'w') as file:
            file.write(json.dumps(dot_gazeru))
        return self
