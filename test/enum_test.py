from enum import Enum, unique
import req_builder

@unique
class Aim(Enum):
    INDEX = req_builder.UserIndexReqBuilder


builder = Aim.INDEX.value
url = builder()
print(url.get_url())
