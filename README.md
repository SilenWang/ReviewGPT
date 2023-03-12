# ReviewGPT

科研人员日常需要对进行大量的文献阅读以跟进最新的研究进度, 但是研究结果的碎片化程度比Linux发行版更甚, 这一定程度上拖慢了科研工作的速度, 本项目旨在利用chatGPT完成一些科研文献检索, 阅读过程中的工作, 使相关工作能更快速高效.

## 运行展示

- 文献准入判断:

![run](img/run.gif)

![demo](img/demo.png)

## 规划内容

- 前端: 使用pynecone构建Web APP
  + [x] 一个勉强能用的基本App
  + [ ] 前端设置API_KEY(安全问题咋保证?)
  + [ ] 部署到`pynecone.app`
  + [ ] 增加原始解析数据下载按钮
  + [ ] 页面布局优化
- 后端: 
  + [ ] 调用chatGPT的API进行内容综述
  + [x] 调用chatGPT的API进行文献内容准入判断(Meta分析用)
  + [x] 调用biopython的API从PUBMED获取文献题录及摘要
  + [ ] 原始解析数据保存并打包
  + [ ] 增加内容准入判断的多次重复(检查结果是否稳定)
  + [ ] 增加RIS文件上传解析的支持

## 其他

- pynecone启动后CPU持续占用, 不知道是什么问题, 解决不了可能会换更简单的前端框架