select_speaker_message_template = """
You are in a role play game. The following roles are available:
{roles}.
Read the following conversation.
Then select the next role from {agentlist} to play. Only return the role."""

select_speaker_prompt_template =  "Read the above conversation. Then select the next role from {agentlist} to play. Only return the role."

select_speaker_auto_multiple_template = """
You provided more than one name in your text, please return just the name of the next speaker. To determine the speaker use these prioritised rules:
1. If the context refers to themselves as a speaker e.g. "As the..." , choose that speaker's name
2. If it refers to the "next" speaker name, choose that name
3. Otherwise, choose the first provided speaker's name in the context
The names are case-sensitive and should not be abbreviated or changed.
Respond with ONLY the name of the speaker and DO NOT provide a reason."""

select_speaker_auto_none_template = """
You didn't choose a speaker. As a reminder, to determine the speaker use these prioritised rules:
1. If the context refers to themselves as a speaker e.g. "As the..." , choose that speaker's name
2. If it refers to the "next" speaker name, choose that name
3. Otherwise, choose the first provided speaker's name in the context
The names are case-sensitive and should not be abbreviated or changed.
The only names that are accepted are {agentlist}.
Respond with ONLY the name of the speaker and DO NOT provide a reason."""