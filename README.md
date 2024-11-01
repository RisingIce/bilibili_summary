# bilibili_summary

### 简介

本项目旨在通过使用OpenAI API调用大型语言模型（LLM），实现对B站视频内容的总结功能。目前项目有两种使用方式，一是使用FastAPI构建的纯后端服务，通过API的形式去调用总结功能，其中，后端支持流式输出和非流式输出两种模式。二是使用Streamlit搭建的简洁直观的UI界面。

**详细了解链接**：[使用大模型总结B站视频 | RisingIce (imrising.cn)](https://www.imrising.cn/posts/2024/0913)

### 安装步骤

1.安装环境

```bash
#clone本仓库到服务器中
git clone https://github.com/RisingIce/bilibili_summary.git

#创建虚拟环境(目前仅测试了py3.10 其他版本自行测试)
conda create -n env_name python=3.10

#激活环境
conda activate env_name

#安装环境
pip install -r requirement.txt
```

2.填写相关的配置文件参数，配置文件位于`/bilibili_summary/server/config.py`

3.启动项目

```bash
#启动FastAPI服务
uvicorn main:app --host 0.0.0.0 --port 3010

#启动Streamlit服务
streamlit run streamlit_ui/summary_ui.py
```

### 使用方法

1.API调用

请求路径：/bilismmary

请求标头：application/json

请求方法：POST

请求参数：

|  参数  | 参数类型 |                  说明                   |
| :----: | :------: | :-------------------------------------: |
| bv_id  |   str    |              B站视频的bv号              |
| prompt |   str    | 喂给LLM的总结Prompt，不写则采用默认参数 |
| stream |   bool   |      是否开启流式输出，默认为False      |

响应参数（非流式）：

|  参数  | 参数类型 |      说明      |
| :----: | :------: | :------------: |
|  avid  |   int    |   视频的avid   |
|  bvid  |   str    |   视频的bvid   |
|  cid   |   int    |  视频的分Pid   |
| title  |   str    |   视频的标题   |
|  url   |   str    |   视频的链接   |
| answer |   str    | 视频的总结内容 |

非流式请求示例：

```json
{
    "bv_id":"BV1Wd4YeZEqG"
}
```

非流式响应示例：

```json
{
    "avid": 113115312168779,
    "bvid": "BV1Wd4YeZEqG",
    "cid": 25640244589,
    "title": "国足1:2不敌沙特，天胡开局也能崩盘？",
    "url": "https://www.bilibili.com/video/BV1Wd4YeZEqG",
    "answer": "核心观点：\n视频主要讨论了中国足球队在与沙特队的比赛中，尽管开局有利，但最终以1:2不敌沙特，引发了关于教练伊万和中国足球未来的讨论。\n\n关键人物/事件：\n1. 伊万（教练）\n2. 中国队与沙特队的比赛\n3. 马图伊迪哈（法国世界杯冠军成员，观看比赛）\n\n主线内容：\n视频首先介绍了比赛前的氛围和球场的特点，随后详细描述了比赛的过程，包括中国队开局的有利情况和沙特队的红牌事件。接着，视频记录了比赛中的关键瞬间和球迷的反应，最终中国队被绝杀，赛后球场响起了要求教练下课的声音。\n\n个人看法：\n视频内容反映了足球比赛的不确定性和球迷的情感波动。尽管中国队开局有利，但最终失利，这凸显了足球比赛的不可预测性。个人认为，视频成功捕捉了比赛的紧张氛围和球迷的热情，但也暴露了中国足球在技术和战术上的不足。支持这一观点的原因是，视频中的比赛结果和球迷反应都指向了中国足球需要改进的方面。"
}
```

流式请求示例：

```json
{
    "bv_id":"BV1kE4HesEUP",
    "stream":true
}
```

流式响应示例（部分）：

![](https://img.picgo.net/2024/09/13/image13b42cbd56f24b48.png)

2.使用StreamlitUI

打开项目streamlit地址：http://yourip:8502

界面如下：

![](https://img.picgo.net/2024/09/13/image5ee256bf1e341474.png)

![](https://img.picgo.net/2024/09/13/image4cac0652b27e4bd8.png)

![](https://img.picgo.net/2024/09/13/imagedc977872d91c2205.png)