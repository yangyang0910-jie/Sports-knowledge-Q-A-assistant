# 运动健康 AI 智能问答系统

基于 **FastAPI + LangChain + RAG** 构建的运动健康领域智能聊天服务。支持用户注册登录、SSE 流式对话、意图识别、混合检索（向量 + BM25 + RRF 融合 + 重排序）、历史对话压缩与多轮记忆。

## 功能特性

- **用户模块**：邮箱注册、密码登录、邮箱验证码登录、JWT 身份认证、Token 黑名单登出
- **智能对话**：SSE 流式输出，意图识别自动区分「领域问题 / 闲聊」
- **RAG 检索增强**：
  - 向量检索（ChromaDB）
  - 关键词检索（BM25）
  - RRF（倒数排名融合）合并两路召回
  - Rerank 重排序模型精排，取 Top-K 送入大模型
- **历史记忆管理**：会话历史保存、查询、删除、搜索，长对话自动压缩为摘要，控制上下文长度
- **健康检查**：`/health` 接口 + Docker HEALTHCHECK

## 技术栈

| 类别 | 技术 |
| --- | --- |
| Web 框架 | FastAPI、Uvicorn |
| 编排框架 | LangChain（Runnable / LCEL） |
| 大模型 | 阿里云 DashScope（OpenAI 兼容模式） |
| 向量数据库 | ChromaDB |
| 关系数据库 | MySQL（PyMySQL） |
| 认证 | JWT（python-jose）、Passlib/bcrypt |
| 向量化 | sentence-transformers / FlagEmbedding |
| 部署 | Docker 多阶段构建 |

## 项目结构

```
fastApiProject/
├── main.py                    # 应用入口，路由注册与 CORS 配置
├── dockerfile                 # Docker 多阶段构建文件
├── requirements.txt           # Python 依赖
├── common/
│   └── MySQLCommon.py         # MySQL 连接公共模块
├── users/                     # 用户模块（注册 / 登录）
│   ├── controller/            # 路由层
│   ├── service/               # 业务逻辑层
│   ├── dao/                   # 数据访问层
│   ├── entity/                # 请求实体
│   └── util/                  # 工具类
├── chat/                      # 聊天模块（RAG 问答 / 历史记录）
│   ├── controller/            # ChatController、HistoryController
│   ├── service/               # ChatService、HistoryService
│   ├── dao/                   # 会话存取、摘要压缩
│   ├── entity/                # 请求实体
│   └── util/                  # 模型加载、BM25、RRF、Rerank、JWT 等工具
├── data/                      # 运动健康领域知识库源数据（CSV）
│   ├── exercise.csv           # 运动项目
│   ├── food.csv               # 食物营养
│   ├── Muscle.csv             # 肌肉知识
│   ├── MuscleTraining.csv     # 力量训练
│   ├── ObesityTreatment.csv   # 肥胖治疗
│   ├── ReduceFat.csv          # 减脂
│   ├── Stretch.csv            # 拉伸
│   └── Synthesize.csv         # 综合知识
└── sports_chroma/             # ChromaDB 向量库持久化目录
```

## 环境准备

### 前置依赖

- Python 3.12+
- MySQL 数据库
- DashScope API Key（或其他 OpenAI 兼容服务）

### 环境变量

在项目根目录创建 `.env` 文件：

```env
# MySQL 配置
MY_HOST=127.0.0.1
MY_PORT=3306
MY_USER=root
MY_PASSWORD=your_password
MY_DATABASE=your_database
MY_CHARSET=utf8mb4

# 大模型配置（OpenAI 兼容）
OPENAI_API_KEY=your_api_key
```

## 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 .env 环境变量（见上一节）

# 3. 准备向量库（首次需要将 data/ 下 CSV 灌入 ChromaDB）

# 4. 启动服务
python main.py
```

服务启动后访问：

- 服务地址：<http://localhost:8000>
- 交互式 API 文档（Swagger）：<http://localhost:8000/docs>
- ReDoc 文档：<http://localhost:8000/redoc>

### Docker 部署

```bash
# 构建镜像
docker build -t sports-ai .

# 运行容器
docker run -d \
  --name sports-ai \
  -p 8000:8000 \
  --env-file .env \
  sports-ai
```

容器内置健康检查，每 30 秒探测一次 `/health`。

## API 接口

### 系统

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |

### 用户模块（/users）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/users/register` | 邮箱注册 |
| POST | `/users/login` | 密码登录 |
| GET | `/users/sendcode?email=` | 发送邮箱验证码 |
| GET | `/users/checkcode?email=&code=` | 校验验证码 |

### 聊天模块（/chat，需携带 Token）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/chat/chat?question=&dialogueId=` | 流式对话（SSE），`dialogueId=0` 表示新会话 |
| POST | `/chat/saveConversation` | 保存一轮问答到历史 |
| POST | `/chat/logout` | 登出（Token 加入黑名单） |

### 历史模块（/history，需携带 Token）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/history/historyMenu` | 获取当前用户会话列表 |
| GET | `/history/queryOneHistory?dialogueId=` | 查询单个会话的完整消息 |
| GET | `/history/deleteOneHistory?dialogueId=` | 删除某条历史记录 |
| GET | `/history/searchMenu?question=` | 按关键词搜索历史会话 |

> 认证方式：登录成功后获取 JWT，后续请求在请求头中携带 `Authorization: Bearer <token>`。

## RAG 处理流程

```
用户问题
   │
   ▼
意图识别（判断是否与运动健康领域相关）
   │
   ├── 不相关 ──→ 直接拼历史上下文 → 大模型生成 → 流式返回
   │
   └── 相关
        │
        ▼
   混合检索（并行两路召回）
        ├── 向量检索：ChromaDB（Top 5）
        └── 关键词检索：BM25（Top 10）
        │
        ▼
   RRF 融合排序
        │
        ▼
   Rerank 重排序 → 取 Top 5
        │
        ▼
   拼装提示词（问题 + 检索内容 + 历史记录 + 压缩摘要）
        │
        ▼
   大模型流式生成 → SSE 返回前端
```

会话保存后，后台线程检查历史长度，超出阈值时自动将旧消息压缩为摘要，用于替代原始历史，控制上下文 token 消耗。

## 跨域配置

当前 CORS 白名单为 `http://localhost:8080`，如需修改其他前端域名，请调整 `main.py` 中的 `allow_origins`。

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
```
