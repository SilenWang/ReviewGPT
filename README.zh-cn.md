# ReviewGPT

科研人员日常需要对进行大量的文献阅读以跟进最新的研究进度, 但是研究结果的碎片化程度比Linux发行版更甚, 这一定程度上拖慢了科研工作的速度, 本项目旨在利用chatGPT完成一些科研文献检索, 阅读过程中的工作, 使相关工作能更快速高效.

## 运行展示

现在可以在Huggingface上试用本程序的[Demo](https://huggingface.co/spaces/SilenWang/ReviewGPT)(需要自备OpenAI API Key)

- 文献准入判断(Screen):

![demo](img/screen.png)

- 文献内容小结(Summarise):

![demo](img/summarise.png)

## 规划内容


- 前端: 使用gradio构建简易WebAPP
  + [x] 一个勉强能用的基本App
  + [x] 前端设置API_KEY(安全问题咋保证?)
  + [ ] 增加原始解析数据下载按钮(json)
  + [x] 内容综述功能实装
  + [ ] 增加About页
  + [ ] 增加使用说明(具体怎么加没想好)
  + [ ] 增加单文献阅读的页面
- 后端: 
  + [x] 调用chatGPT的API进行内容综述
  + [x] 调用chatGPT的API进行文献内容准入判断(Meta分析用)
  + [x] 调用biopython的API从PUBMED获取文献题录及摘要
  + [ ] 原始解析数据保存并打包
    * ~~ 这里有涉及数据安全问题, 需要了解下返回的id是否会导致Key泄露? ~~
  + [ ] ~~ 增加内容准入判断的多次重复(检查结果是否稳定) ~~
  + [x] 增加RIS文件上传解析的支持
  + [ ] 增加chatGPT以外的模型支持
    + [ ] chatGLM
    + [ ] moss
    + [ ] LLaMA
  + [x] 增加单文献阅读的功能
  + [ ] 增加现有功能的API
- 参考学习:
  + [ ] 学习[ResearchGPT](https://github.com/mukulpatnaik/researchgpt)的内容, 增加类似的功能
  + [ ] 学习[chatPaper](https://github.com/kaixindelele/ChatPaper)的内容, 增加类似的功能
  + [ ] 尝试构建个[chatPDF](https://www.chatpdf.com/)类似的功能
- 杂项:
  - [x] 英文README
  - [ ] 准备Dockfile, 构建容器
  - [x] 准备HuggingFace Demo
  - [ ] 效仿[chatPaper](https://github.com/kaixindelele/ChatPaper)增加网络任务的错误处理(tenacity)

## 学习内容

### ResearchGPT功能实现原理

- 借助chatGPT解读可知, ResearchGPT的实现方式为:
  + 将文件内容**按页**转换为文本
  + 调用`text-embedding-ada-002`进行文本embedding矩阵计算
  + 将问题也转换为矩阵, 与每个页面的矩阵计算相似性
  + 将相似性最高的3个页面与提出的问题一起给chatGPT接口, 实现文献解读

## 问题记录

- 本项目最初采用pynecone开发, 但是碰到了若干影响使用/观感的问题, 因此最后转到了gradio
  - pynecone启动后CPU持续占用
  - 目前上传文件功能不是特别好用, 必须要用按钮或其他内容来触发上传(没找到如何实现拖拽即上传)
  - 上传文件后, 进行其他操作会使得已显示的文件名丢失