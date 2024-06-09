# Account

Types:

```python
from alphakek.types import User
```

Methods:

- <code title="get /account">client.account.<a href="./src/alphakek/resources/account.py">info</a>() -> <a href="./src/alphakek/types/user.py">User</a></code>

# Knowledge

Types:

```python
from alphakek.types import KnowledgeDocumentView, KnowledgeSearchResponse
```

Methods:

- <code title="get /knowledge/get/by_link">client.knowledge.<a href="./src/alphakek/resources/knowledge.py">get_by_link</a>(\*\*<a href="src/alphakek/types/knowledge_get_by_link_params.py">params</a>) -> <a href="./src/alphakek/types/knowledge_document_view.py">KnowledgeDocumentView</a></code>
- <code title="post /knowledge/search">client.knowledge.<a href="./src/alphakek/resources/knowledge.py">search</a>(\*\*<a href="src/alphakek/types/knowledge_search_params.py">params</a>) -> <a href="./src/alphakek/types/knowledge_search_response.py">KnowledgeSearchResponse</a></code>

# Chat

## Completion

Types:

```python
from alphakek.types.chat import ChatCompletion
```

Methods:

- <code title="post /v1/chat/completions">client.chat.completion.<a href="./src/alphakek/resources/chat/completion.py">create</a>(\*\*<a href="src/alphakek/types/chat/completion_create_params.py">params</a>) -> <a href="./src/alphakek/types/chat/chat_completion.py">ChatCompletion</a></code>
