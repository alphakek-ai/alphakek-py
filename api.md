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
from alphakek.types import KnowledgeDocumentView, KnowledgeSearchResponse, KnowledgeAskResponse
```

Methods:

- <code title="post /knowledge/ask">client.knowledge.<a href="./src/alphakek/resources/knowledge.py">ask</a>(\*\*<a href="src/alphakek/types/knowledge_ask_params.py">params</a>) -> <a href="./src/alphakek/types/knowledge_ask_response.py">KnowledgeAskResponse</a></code>
- <code title="get /knowledge/get/by_link">client.knowledge.<a href="./src/alphakek/resources/knowledge.py">get_by_link</a>(\*\*<a href="src/alphakek/types/knowledge_get_by_link_params.py">params</a>) -> <a href="./src/alphakek/types/knowledge_document_view.py">KnowledgeDocumentView</a></code>
- <code title="post /knowledge/search">client.knowledge.<a href="./src/alphakek/resources/knowledge.py">search</a>(\*\*<a href="src/alphakek/types/knowledge_search_params.py">params</a>) -> <a href="./src/alphakek/types/knowledge_search_response.py">KnowledgeSearchResponse</a></code>

# Chat

## Completions

Types:

```python
from alphakek.types.chat import ChatCompletion, CompletionCreateResponse
```

Methods:

- <code title="post /v1/chat/completions">client.chat.completions.<a href="./src/alphakek/resources/chat/completions.py">create</a>(\*\*<a href="src/alphakek/types/chat/completion_create_params.py">params</a>) -> <a href="./src/alphakek/types/chat/completion_create_response.py">CompletionCreateResponse</a></code>

# Visuals

Methods:

- <code title="post /visuals/apply_effect">client.visuals.<a href="./src/alphakek/resources/visuals.py">apply_effect</a>(\*\*<a href="src/alphakek/types/visual_apply_effect_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="post /visuals/apply_mirage">client.visuals.<a href="./src/alphakek/resources/visuals.py">apply_mirage</a>(\*\*<a href="src/alphakek/types/visual_apply_mirage_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="post /visuals/create_image">client.visuals.<a href="./src/alphakek/resources/visuals.py">create_image</a>(\*\*<a href="src/alphakek/types/visual_create_image_params.py">params</a>) -> BinaryAPIResponse</code>
