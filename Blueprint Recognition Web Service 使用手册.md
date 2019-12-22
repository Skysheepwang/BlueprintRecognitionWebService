# Blueprint Recognition Web Service 文档

## 概览

### 项目概览

本项目是对清华大学软件学院张荷花老师图纸关键元素识别项目组内图纸识别工作内容的整合，提供了上传图纸、处理结果的在线查看和下载功能。

使用Python Django框架，前端使用了Bootstrap工具包。

GitHub：<https://github.com/Skysheepwang/BlueprintRecognitionWebService> 

### 心得分享

可以查看作者的个人博客： skysheepwang.github.io



## 项目背景

在图纸关键元素识别项目组里的前辈们已经完成了很多工作，如李旭学长对图纸上部分构件的识别、张庭瑞学长对墙体等空间信息的识别、杨婧学姐对文本信息的识别等，这些工作已经有了阶段性进展，有着很好的效果。

然而，它们中的部分工作尚未进行良好的可视化工作，难以直观地看到效果；同时，它们同为对图纸关键元素的识别的工作，但未进行整合，不便于老师的统一把控以及对外展示工作。

因此，本项目着重于对这些工作进行整合并提供方便的可视化展示，方便开发者的调试、老师的察看和面向客户的汇报展示。

在未来，本项目可能会作为一个对外服务，被实际有着对图纸识别需求的客户所使用；在此基础上还需要对用户行为做更深层次的分析，同时并发量等指标也在需要考量的范畴中，相关的工具如数据库等将会加入项目之中。



## 项目结构

项目包含两个主要页面：

### 主页面

TODO Screenshot

主页面包括：用户上传图纸的接口，历史全部上传过的图纸列表，开始各个处理的按钮，跳转到该图纸查看页面的按钮，下载该图纸处理结果的按钮。

TODO Screenshot

已经完成相应处理的话按钮会变色。

TODO Screenshot

下载会以.zip格式压缩包的形式，其中文件格式为：

BlueprintName.zip

-- blueprints

​	-- blueprint.pdf

-- media

​	-- blueprint.jpg

​	-- blueprint_member.jpg

​	-- blueprint_space.jpg

​	-- blueprint_text.jpg

-- jsons

​	-- blueprint_member.json

​	-- blueprint_space.json

​	-- blueprint_text.json



### 查看页面

TODO Screenshot

查看页面主要包括：图纸处理结果概览、

