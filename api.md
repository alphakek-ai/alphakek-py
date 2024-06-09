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

- <code title="post /knowledge/search">client.knowledge.<a href="./src/alphakek/resources/knowledge/knowledge.py">search</a>(\*\*<a href="src/alphakek/types/knowledge_search_params.py">params</a>) -> <a href="./src/alphakek/types/knowledge_search_response.py">KnowledgeSearchResponse</a></code>

## Get

Methods:

- <code title="get /knowledge/get/by_link">client.knowledge.get.<a href="./src/alphakek/resources/knowledge/get.py">by_link</a>(\*\*<a href="src/alphakek/types/knowledge/get_by_link_params.py">params</a>) -> <a href="./src/alphakek/types/knowledge_document_view.py">KnowledgeDocumentView</a></code>

# Chats

Types:

```python
from alphakek.types import ChatCompletion
```

Methods:

- <code title="post /v1/chat/completions">client.chats.<a href="./src/alphakek/resources/chats.py">completions</a>(\*\*<a href="src/alphakek/types/chat_completions_params.py">params</a>) -> <a href="./src/alphakek/types/chat_completion.py">ChatCompletion</a></code>
