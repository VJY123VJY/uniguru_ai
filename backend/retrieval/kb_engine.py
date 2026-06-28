from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, Optional, List


logger = logging.getLogger(__name__)


class SovereignRetriever:
    """
    Improved Retrieval Engine for UniGuru.

    Features:
    - keyword matching
    - title matching
    - category matching
    - query expansion
    - better scoring
    - lower false rejection
    """

    def __init__(self, index_path: Optional[str] = None):

        self.index_path = index_path or os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "knowledge",
                "index",
                "master_index.json"
            )
        )

        self.index: Dict[str, Any] = {}

        self._load_index()


    # ----------------------------
    # Load index
    # ----------------------------

    def _load_index(self):

        if not os.path.exists(self.index_path):

            logger.warning(
                "Index missing %s",
                self.index_path
            )

            self.index = {}
            return


        try:

            with open(
                self.index_path,
                "r",
                encoding="utf-8-sig"
            ) as f:

                raw = f.read()


            try:
                loaded = json.loads(raw)

            except json.JSONDecodeError:

                repaired = re.sub(
                    r"\\(?![\\\"/bfnrtu])",
                    "/",
                    raw
                )

                loaded = json.loads(repaired)


            if isinstance(loaded, dict):

                self.index = loaded

                logger.info(
                    "Index loaded. Keywords: %s",
                    len(self.index)
                )


            else:

                self.index = {}


        except Exception as e:

            logger.error(
                "Index load error %s",
                e
            )

            self.index = {}



    # ----------------------------
    # Normalize text
    # ----------------------------

    def normalize(self,text):

        return set(
            re.sub(
                r"[^\w\s]",
                "",
                text.lower()
            ).split()
        )



    # ----------------------------
    # Query expansion
    # ----------------------------

    def expand_query(self,query):

        query=query.lower()

        mapping={


            "biography":[
                "life",
                "history",
                "born",
                "biography",
                "about"
            ],


            "swaminarayan":[
                "bhagwan",
                "baps",
                "akshar",
                "purushottam",
                "gunatitanand"
            ],


            "moksha":[
                "salvation",
                "liberation"
            ]
        }


        words=query.split()


        expanded=set(words)


        for word in words:

            if word in mapping:

                expanded.update(
                    mapping[word]
                )


        return " ".join(expanded)




    # ----------------------------
    # Score document
    # ----------------------------

    def score_document(
        self,
        query,
        keyword,
        entry
    ):


        score=0


        query_words=self.normalize(query)


        keyword_words=self.normalize(keyword)



        # keyword match

        score += len(
            query_words.intersection(
                keyword_words
            )
        ) * 3



        if isinstance(entry,dict):


            title=str(
                entry.get(
                    "title",
                    ""
                )
            )


            category=str(
                entry.get(
                    "category",
                    ""
                )
            )


            content=str(
                entry.get(
                    "content",
                    ""
                )
            )



            # title boost

            title_words=self.normalize(title)

            score += len(
                query_words.intersection(title_words)
            ) * 5



            # category boost

            category_words=self.normalize(category)

            score += len(
                query_words.intersection(category_words)
            ) * 4



            # content match

            content_words=self.normalize(content)

            score += len(
                query_words.intersection(content_words)
            )



        return score




    # ----------------------------
    # Main query
    # ----------------------------

    def query(
        self,
        user_query:str
    ):


        expanded_query=self.expand_query(
            user_query
        )


        logger.info(
            "Original query: %s",
            user_query
        )


        logger.info(
            "Expanded query: %s",
            expanded_query
        )


        best=None
        best_score=0



        for keyword,entries in self.index.items():


            if not isinstance(entries,list):
                continue


            for entry in entries:


                score=self.score_document(
                    expanded_query,
                    keyword,
                    entry
                )


                if score > best_score:

                    best_score=score

                    best={
                        "keyword":keyword,
                        "entry":entry
                    }



        logger.info(
            "Best score: %s",
            best_score
        )



        # LOWER threshold

        if best and best_score >= 2:


            entry=best["entry"]


            if not isinstance(entry,dict):

                entry={}



            metadata=entry.get(
                "metadata",
                {}
            )


            if not isinstance(metadata,dict):

                metadata={}



            return {


                "answer":
                    entry.get(
                        "content",
                        ""
                    ),


                "source_file":
                    metadata.get(
                        "source"
                    ),


                "confidence_level":
                    round(
                        min(
                            best_score/10,
                            1
                        ),
                        2
                    ),


                "verified":True

            }



        return {


            "answer":
            "I do not have verified knowledge to answer this question.",


            "source_file":None,


            "confidence_level":0,


            "verified":False

        }




_engine=SovereignRetriever()



def retrieve(query:str):

    return _engine.query(query)