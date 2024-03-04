# bedrock_agent_konwledege_base

### Demo 介绍

模拟预订机票业务，业务流程如下所示

收集行程信息 -》 查询指定日期航班并展示 -》确认航班号后自动预订 -》 自动发送发票邮件

### Workshop
待更新。。。

### 代码结构说明 
```
├── README.md
├── conf
│   ├── DejaVuSansCondensed.ttf                          # PDF 字体文件
│   └── ticket.faq                                       # 自建检索库，问答源文件
├── boook_ticket_lambda.py                               # demo 业务代码实现文件，lambda function
├── book_ticket_lambda_layer.zip                         # demo python 依赖包，lambda layer
├── ticket_service_schema.json                           # Lambda API schema
├── notebooks
│   ├── bedrock_agent_example.ipynb                      # 完整创建 Agent
│   └── knowledge_base.ipynb                             # 完整创建 knowledge base
└── requirements.txt
```

### Enviroment
基础环境：python 3.11

#### python 依赖打包
本demo代码已经有打包好的lambda_layer文件，直接上传S3即可

如果有自己需要打包其他依赖，可使用 lambda image 安装依赖库, 上传到 lambda_layer

reference link :https://repost.aws/knowledge-center/lambda-layer-simulated-docker

可以找一台EC2，在EC2的Linux环境打包，命令如下

```
mkdir layer
cp requirements.txt layer/requirements.txt
docker run -ti -v $(pwd)/layer:/app -w /app --entrypoint /bin/bash public.ecr.aws/lambda/python:3.11 -c "pip3 install --taget ./python -r requirements.txt"
zip -r lambda_layer.zip python
```

### 上传 conf 文件到 s3 bucket
- Console 上传
- Notebook 上传

### 开通 AWS SES 服务

如果是使用 console 创建 Agent 需要执行2，3 步，如果是 notebook 创建则不需要做，已经包含在 notebook 的代码块中，顺序执行即可。

1. verify 邮箱，链接https://us-east-1.console.aws.amazon.com/ses/home?region=us-east-1#/get-set-up
2. 注意测试过程中，提供的收件人邮箱也需要使用验证后的邮箱，收件人和发件人可以是同一人


### 创建 Agent
可以有两种方式创建：

1. Console 创建
    - 创建 lambda function: 
        * 添加 book_ticket_lambda.py 内容到 lambda 代码编辑处
        * 添加 book_ticket_lambda_layer.zip 到 lambda layer
        * 修改添加 lambda Environment Variables, BUCKET_NAME = "你构建的s3 bucket", SENDER="验证的邮箱"
        * 点击 deploy
    - 创建 Agent，根据 console 的指示，一步步创建关联即可，Agent instruction 可在下面找到

2. Notebook step by step 创建
    - 根据 notebook 的顺序一步步执行即可

#### Agent instructions
You are a friendly invoice assistant. When greeted, answer user with "I'm an invoice assistant". Through the "InvoiceService" action group, you can offer invoice services. When generating an invoice, first collect all required invoice information from user. Then generate invoice preview information for the user's reference and return text_info from the function result to user. Confirm with user if they want to proceed with generating the actual invoice. If user confirms, use function to generate an invoice formally and return the downloadUrl from the function result to user. This allows user to download the invoice. If user indicates the information is incorrect, ask them to provide corrected information and generate preview infomation again. Finally confirm if the user needs the invoice sent to a designated email address, if so, email the invoice file to the address provided.
