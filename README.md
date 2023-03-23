# ReviewGPT

科研人员日常需要对进行大量的文献阅读以跟进最新的研究进度, 但是研究结果的碎片化程度比Linux发行版更甚, 这一定程度上拖慢了科研工作的速度, 本项目旨在利用chatGPT完成一些科研文献检索, 阅读过程中的工作, 使相关工作能更快速高效.

## 运行展示

- 文献准入判断:

<!-- ![run](img/run.gif) -->

![demo](img/demo.png)

## 规划内容


- 可能是处于项目早期, pynecone开发中出现过若干问题, 为了更快的开发, 转用gradio进行实现, 后续再考虑用别的框架来写

- 前端: 使用gradio构建简易WebAPP
  + [x] 一个勉强能用的基本App
  + [ ] 前端设置API_KEY(安全问题咋保证?)
  + [ ] 增加原始解析数据下载按钮
  + [ ] 内容综述功能实装
  + [ ] 增加About页
  + [ ] 增加使用说明(具体怎么加没想好)
- 后端: 
  + [x] 调用chatGPT的API进行内容综述
  + [x] 调用chatGPT的API进行文献内容准入判断(Meta分析用)
  + [x] 调用biopython的API从PUBMED获取文献题录及摘要
  + [ ] 原始解析数据保存并打包
    * 这里有涉及数据安全问题, 需要了解下返回的id是否会导致Key泄露? 
  + [ ] ~~增加内容准入判断的多次重复(检查结果是否稳定)~~
  + [x] 增加RIS文件上传解析的支持
  + [ ] 增加chatGPT以外的模型支持(如chatGLM, moss, LLaMA)
  + [ ] 学习[ResearchGPT](https://github.com/mukulpatnaik/researchgpt)的内容, 增加类似的功能

## 其他

- pynecone启动后CPU持续占用, 不知道是什么问题, 解决不了可能会换更简单的前端框架
- 目前上传文件功能不是特别好用, 必须要用按钮或其他内容来出发, 多点一下非常麻烦, 同时如果点了其他位置, 页面会再次刷新