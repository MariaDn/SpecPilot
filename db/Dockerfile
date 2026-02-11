FROM pgvector/pgvector:pg16

RUN apt-get update && apt-get install -y \
    curl \
    hunspell-uk \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/share/postgresql/16/tsearch_data/

RUN cp /usr/share/hunspell/uk*.dic /usr/share/postgresql/16/tsearch_data/uk_ua.dict || \
    cp /usr/share/hunspell/uk*.dict /usr/share/postgresql/16/tsearch_data/uk_ua.dict
    
RUN cp /usr/share/hunspell/uk*.aff /usr/share/postgresql/16/tsearch_data/uk_ua.affix

RUN curl -L -o /usr/share/postgresql/16/tsearch_data/ukrainian.stop \
    https://raw.githubusercontent.com/vshymanskyy/utxt/master/stop-words/ukrainian.txt

RUN chown postgres:postgres /usr/share/postgresql/16/tsearch_data/uk_ua.*
RUN chown postgres:postgres /usr/share/postgresql/16/tsearch_data/ukrainian.stop