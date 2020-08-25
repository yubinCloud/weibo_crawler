# weibo_curl 文档说明

## 介绍

对微博数据进行爬取

## 返回结果格式：

```
{
    'error_code':0,
    'data':{
        'result': {} or [],
        'cursor': str
    },
    'error_msg':''
}
```

## API

### 1. 推文搜索接口

+ 根据关键字搜索推文
+ 路由：`/weibo_curl/api/search_tweets`

#### 请求参数

URL参数：

| key     | description                        | 是否必选                        | example    |
| ------- | ---------------------------------- | ------------------------------- | ---------- |
| keyword | 搜索关键字                         | 是                              | '新冠肺炎' |
| cursor  | 搜索第几页                         | 否，默认第一页                  | 2          |
| is_hot  | 是否搜索热门微博，1表示是，0表示否 | 否，默认为False，即搜索普通微博 | 1          |

#### 返回格式

成功时返回json的 `result` 字段为一个l由多个dict组成的list，每个dict代表一条微博，每个元素(dict)的格式如下：(每个字段默认值均为空字符串)

| key             | description                  | value type      | example                               |
| --------------- | ---------------------------- | --------------- | ------------------------------------- |
| weibo_id        | 微博id                       | str             | 'Jhv4a7KAd'                           |
| user_id         | 用户的id                     | str             | '6004281123'                          |
| screen_name     | 用户名                       | str             | '21世纪经济报道'                      |
| text            | 微博内容                     | str             | '#新冠康复者二次...'                  |
| article_url     | 头条文章url                  | str             | ""                                    |
| location        | 发布位置                     | str             | ""                                    |
| at_users        | 艾特的用户，无艾特时为空列表 | [str, str, ...] | ['梨视频体育']                        |
| topics          | 话题                         | str             | '一名新冠肺炎康复者4个多月后二次感染' |
| reposts_count   | 转发数                       | str             | '65'                                  |
| comments_count  | 评论数                       | str             | '33'                                  |
| attitudes_count | 点赞数                       | str             | '14'                                  |
| created_at      | 创建时间                     | str             | '2020-08-25 09:12'                    |
| source          | 发布工具                     | str             | 'iPhone客户端'                        |
| pics            | 图片url                      | str             | ''                                    |
| video_url       | 视频url                      | str             | ''                                    |
| reteet_id       | 转发微博的id                 | str             | ''                                    |

### 2. 推文展示接口

+ 根据推文id搜索推文
+ 路由： `/weibo_curl/api/statuses_show`

#### 请求参数

URL参数：

| key      | description                                                  | 是否必选             | example      |
| -------- | ------------------------------------------------------------ | -------------------- | ------------ |
| weibo_id | 微博id                                                       | 是                   | '1669879400' |
| cursor   | 查询第几页                                                   | 否，默认第一页       | 2            |
| hot      | (暂时无效，还只能获取普通评论)表示获取热评还是获取普通评论，普通评论在第一页包含少数热评，其余为最新评论 | 否，默认获取普通评论 | 1            |

#### 返回格式

成功时返回json的 `result` 字段格式

| key           | value type                                             | description                                               | example         |
| ------------- | ------------------------------------------------------ | --------------------------------------------------------- | --------------- |
| weibo_id      | str                                                    | 微博id                                                    | "Jgs8rlEno"     |
| user_id       | str                                                    | 发布者的id                                                | "1669879400"    |
| user_name     | str                                                    | 发布者的昵称                                              | "Dear-迪丽热巴" |
| original      | bool                                                   | 是否为原创                                                | false           |
| weibo_content | 当original == true时为str；当original == false时为dict | 微博内容，类型为str时即为微博原内容；当类型为dict时见下面 |                 |
|               | list                                                   | 评论列表，每个元素为一个dict，代表一条评论                |                 |

当微博时转发类型时weibo_content为dict类型，其格式：

| key            | value type | description | example             |
| -------------- | ---------- | ----------- | ------------------- |
| retweet        | str        | 转发内容    | "#中国首部海外...." |
| retweet_reason | str        | 转发理由    | "......"            |

comments中每个元素(dict)的格式，每个字段的值为null时表示未提取到该字段：

| key          | value type | description      | example                                            |
| ------------ | ---------- | ---------------- | -------------------------------------------------- |
| is_hot       | bool       | 是否为热评       | true                                               |
| user_id      | str        | 评论用户id       | "1669879400"                                       |
| screen_name  | str        | 评论用户的用户名 | "Swisse斯维诗"                                     |
| content      | str        | 评论内容         | "..."                                              |
| like_num     | str        | 点赞数           | '616'                                              |
| publish_info | str        | 发布信息         | "08月18日 10:09 来自网页" 或者 "2分钟前 来自网页 " |

### 3. 用户搜索接口

+ 说明：根据关键词搜索用户
+ 路由：`/weibo_curl/api/users_search`

#### 请求参数

URL参数：

| key       | description                                                  | 是否必选         | example  |
| --------- | ------------------------------------------------------------ | ---------------- | -------- |
| keyword   | 搜索关键字                                                   | 是               | 迪丽热巴 |
| cursor    | 查询第几页                                                   | 否，默认第1页    | 2        |
| user_type | 查询限制的用户类型，值为1：机构认证， 2：个人认证，3：普通用户，其余值均为无限制 | 否，默认所有用户 | 1        |
| gender    | 查询限制性别，值为0：女性，值为1：男性，其余值均为无限制     | 否，默认无限制   | 0        |
| age_limit | 查询年龄限制，值为1：低于18岁，2：19-22岁，3：30-39岁，4：超过40岁，其余值均为无限制 | 否，默认无限制   | 1        |

#### 返回格式

成功时返回json的 `result` 字段为一个l由多个dict组成的list，每个dict代表一个用户，每个元素(dict)的格式如下：(每个字段默认值均为None，表示未提取到项该信息)

| key             | description    | value type            | example                                                      |
| --------------- | -------------- | --------------------- | ------------------------------------------------------------ |
| user_id         | 用户的id       | str                   | '1669879400'                                                 |
| nickname        | 昵称           | str                   | 'Dear-迪丽热巴'                                              |
| title           | 所拥有的的头衔 | str                   | '微博个人认证'                                               |
| verified_reason | 认证原因       | str                   | '嘉行传媒签约演员\u3000'                                     |
| gender          | 性别           | int                   | 0                                                            |
| location        | 位置           | str                   | '上海 静安区'                                                |
| description     | 简介           | str                   | '简介：一只喜欢默默表演的小透明。工作联系jaywalk@jaywalk.com.cn 🍒' |
| tags            | 标签           | list，[str, str, ...] | ['迪丽热巴', 'Dilraba', '三生三世枕上书', '腾讯视频创造营', '电影日月', '声临其境'] |
| education       | 教育信息       | str                   | '教育信息：上海戏剧学院'                                     |
| work            | 工作信息       | str                   | '职业信息：嘉行传媒'                                         |
| weibo_num       | 微博数         | str                   | '1184'                                                       |
| following       | 关注数         | str                   | '257'                                                        |
| followers       | 粉丝数         | str                   | '7241万'                                                     |



### 4. 用户展示接口

+ 说明：根据用户id搜索用户
+ 路由：`/weibo_curl/api/users_show`

#### 请求参数

URL查询字符串参数:

| key     | description | example      |
| ------- | ----------- | ------------ |
| user_id | 用户id      | '1669879400' |

#### 返回格式

成功时返回json的 `result` 字段格式： 

| key             | description | value type | example                                 |
| --------------- | ----------- | ---------- | --------------------------------------- |
| id              | 用户真实id  | str        | '1669879400'                            |
| nickname        | 昵称        | str        | 'Dear-迪丽热巴'                         |
| gender          | 性别        | str        | '女'                                    |
| location        | 用户所在地  | str        | '上海'                                  |
| birthday        | 生日        | str        | '0001-00-00'                            |
| description     | 用户简介    | str        | '一只喜欢默默表演的小透明。工作联系...' |
| verified_reason | 认证信息    | str        | '嘉行传媒签约演员'                      |
| education       | 学习经历    | str        | '上海戏剧学院'                          |
| work            | 工作经历    | str        | '嘉行传媒 '                             |
| weibo_num       | 微博数      | int        | 1178                                    |
| following       | 关注数      | int        | 257                                     |
| followers       | 粉丝数      | int        | 72325060                                |

### 5. 用户时间线接口

+ 说明：根据用户id搜索用户的推文

+ 路由：`/weibo_curl/api/statuses_user_timeline`

#### 请求参数：

URL查询参数：

| key     | description                                                  | 是否必选 | example      |
| ------- | ------------------------------------------------------------ | -------- | ------------ |
| user_id | 用户id                                                       | 是       | '1669879400' |
| cursor  | 指示本次查询的页数，默认为1                                  | 否       | '2'          |
| filter  | 指示是否爬取转发微博，值为0时爬取全部微博（原创+转发），值为1是只爬取原创微博，默认为0 | 否       | 1            |

#### 返回格式

成功时返回`result`的格式：

| key                | description                                                  | value type | example                                                      |
| ------------------ | ------------------------------------------------------------ | ---------- | ------------------------------------------------------------ |
| id                 | 微博id                                                       | str        | 'Jgs8rlEno'                                                  |
| user_id            | 用户id                                                       | str        | '1669879400'                                                 |
| content            | 微博内容：当微博为原创时，只有一个键值对：`{"weibo_content": '...'}`；当微博为转发的微博时，有三个键值对，`{"retweet_reason": "...", "original_user": "...", "weibo_content": "...."}`, 分别表示`转发理由、原始用户名、转发内容`，其中原始用户名不存在时`original_user`为None | dict       | {'retweet_reason': '转发理由:#中国首部......英雄！', 'original_user': '电影蓝色防线', 'weibo_content': '#中国首部......的微博视频'} |
| article_url        | 头条文章url，没有时为空字符串                                | str        | ''                                                           |
| original_prictures | 原创图片的url，每一个元素为一个图片                          | list       | ['http://ww1.sina...', '....']                               |
| retweet_pictures   | 转发微博的图片url，每一个元素为一个图片                      | list       | ['....', '....']                                             |
| original           | 是否为原创，True表示原创                                     | bool       | True                                                         |
| video_url          | 视频URL，没有时值为"无"                                      | str        | '....'                                                       |
| publish_place      | 微博发布位置，没有时为"无"                                   | str        |                                                              |
| publish_time       | 微博发布时间                                                 | str        | '2020-08-13 17:14'                                           |
| publish_tool       | 微博发布工具，没有时为"无"                                   | str        |                                                              |
| up_num             | 微博点赞数                                                   | int        | 417438                                                       |
| retweet_num        | 微博转发数                                                   | int        | 6174                                                         |
| comment_num        | 微博评论数                                                   | int        | 22449                                                        |

### 6. 用户朋友列表接口（朋友关注的人）

+ 说明：根据用户的id搜索用户朋友，同时也要返回他们的信息
+ 路由：`/weibo_curl/api/friends_list`

#### 请求参数

URL参数：

| key     | description      | 是否必选 | example    |
| ------- | ---------------- | -------- | ---------- |
| user_id | 用户id           | 是       | 1669879400 |
| cursor  | 页数，默认第一页 | 否       | 1          |

#### 返回格式

成功时返回json的 `result` 字段格式：

| key          | value type | description                                | example       |
| ------------ | ---------- | ------------------------------------------ | ------------- |
| friend_list  | array      | 各朋友组成的列表，每个朋友被表示成一个dict | [{}, {}, ...] |
| max_page_num | int        | 最大页数                                   | 10            |

friend_list中每个朋友所封装的dict格式：

| key       | value type | description | example      |
| --------- | ---------- | ----------- | ------------ |
| user_id   | str        | 用户的id    | "7482738083" |
| user_name | str        | 用户名      | "上海发布"   |
| fans_num  | int        | 粉丝数量    | 9332457      |

example:

```json
{
	"error_code": 0,
    "data": {
        "result": {
            "friend_list": [
                {
                    "user_id": "7482738083",
                    "user_name": "繁花BlossomsShanghai",
                    "fans_num": 11952
                },
                {
                    ......
                }
            ]
        },
        "cursor": 2
    },
    "error_msg": null
}
```

### 7. 用户粉丝列表接口

+ 说明：根据用户id搜索用户粉丝
+ 路由： `/weihbo_curl/api/followers_list`

#### 请求参数

URL参数：

| key     | description      | 是否必选 | example    |
| ------- | ---------------- | -------- | ---------- |
| user_id | 用户id           | 是       | 1669879400 |
| cursor  | 页数，默认第一页 | 否       | 1          |

#### 返回格式

成功时返回json的 `result` 字段格式：

| key           | value type | description                                | example       |
| ------------- | ---------- | ------------------------------------------ | ------------- |
| follower_list | array      | 各粉丝组成的列表，每个粉丝被表示成一个dict | [{}, {}, ...] |
| max_page_num  | int        | 最大页数                                   | 10            |

followe_list中每个粉丝代表的dict的格式：

| key       | value type | description | example      |
| --------- | ---------- | ----------- | ------------ |
| user_id   | str        | 用户的id    | "6306674379" |
| user_name | str        | 用户名      | "胡小椒09"   |
| fans_num  | int        | 粉丝数量    | 8            |

example 与朋友列表接口返回的一样。

## 错误类型

```
# URL缺少参数
URL_LACK_ARGS = {
    'error_code': 2001,
    'error_msg': 'URL is lack of arguments.'
}

# URL参数错误
URL_ARGS_ERROR = {
    'error_code': 2002,
    'error_msg': 'URL args error.'
}

# 登录失效
LOGIN_ERROR = {
    'error_code': 2003,
    'error-msg': 'An error occurred while logging in.'
}

# 用户不存在
PAGE_NOT_FOUND = {
    'error_code': 2004,
    'error_msg': "Can't find the page."
}

# 微博网站返回其他错误信息
OTHER_RESP_ERROR = {
    'error_code': 2005,
    'error_msg': "Sina weibo return a error http response."
}

# 未知错误
UNKNOWN_ERROR = {
    'error_code': 2006,
    'error_msg': "An unknown error has occurred here."
}
```