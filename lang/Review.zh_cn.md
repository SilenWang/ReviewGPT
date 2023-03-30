### 使用说明

这个页面提供Summarise和Screen两种功能:

- Summarise: 阅读多篇文章的摘要, 总结摘要的内容并比较多个研究的异同, 可以通过Prompts进行进一步提问
- Screen: 逐一阅读文章的摘要, 判断文章是否符合Prompts中给出的条件, 可用于批量筛选文献

目前提供两种输入方式:

- PMID: 直接输入PMID号, 将调用biopython提供的Pumbed API获取文献摘要并解析
- RIS格式文件: 可从各种文献管理软件, 或者在线数据库以RIS格式导出题录后上传解析