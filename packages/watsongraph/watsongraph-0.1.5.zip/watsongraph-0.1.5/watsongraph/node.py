from mwviews.api import PageviewsClient
import hashlib
import watsongraph.event_insight_lib


class Node:
    """
    The IBM Watson Concept Insights API is based on a weighted graph of Wikipedia pages. Each vertex in the graph
    corresponds to an individual article, referred to as a "node". This "Node" object class abstracts these nodes
    and adds some light Wikipedia-derived syntactic sugar.
    """

    """
    The proper name of the IBM Watson API graph node, e.g. `"/graphs/wikipedia/en-20120601/concepts/IBM_Watson"`.
    """
    node = ""

    """
    The name of the Wikipedia article associated with the node, e.g. Apple, Apple Inc., Nirvana (band), etc.
    "Label" is the terminology used by the IBM Watson API for this attribute; "Concept" is the terminology used
    instead by this library (we are building a `ConceptModel()` not a `LabelModel()`!).
    """
    concept = ""

    """
    The node's parsed display name. Apple is Apple, but so is Apple (band) and Apple (album).
    """
    name = ""

    """
    A raw monthly view count of the Wikipedia article associated with the concept. For speed this parameter is left
    unset unless explicitly set by the `set_view_count()` method.
    """
    view_count = 0

    """
    A measure of the strength of the concept. Left unset explicitly unless manipulated by certain `User` class methods.
    """
    relevance = 0.0

    def __init__(self, concept, view_count=view_count, relevance=relevance):
        """
        :param concept: The raw concept used to initialize the node.
        """
        self.node = "/graphs/wikipedia/en-20120601/concepts/" + concept.replace(' ', '_')
        self.concept = concept
        if "(" in self.concept:
            self.name = concept[:concept.find("(")]
        else:
            self.name = concept
        if view_count:
            self.view_count = view_count
        if relevance:
            self.relevance = relevance
        # The view_count attribute is left unset by default.

    def __eq__(self, other):
        """
        Two nodes are equal when their concept attributes are equivalent.
        """
        if self and other:
            return self.concept == other.concept
        else:
            return False

    def __hash__(self):
        """
        Two concepts have an equivalent hash if their labels are equivalent. Comparison-by-hash is overwritten this
        way to support `nx.compose()` as used in `conceptmodel.merge_with()`.
        """
        return int(hashlib.md5(self.concept.encode()).hexdigest(), 16)

    def hacky_str_rpr(self):
        """
        :return: A concatenated string representation used for ConceptModel data storage. See `conceptmodel.to_json()`,
        `conceptmodel.load_from_json()`.
        """
        return self.concept + '_' + str(self.relevance) + '_' + str(self.view_count)

    def set_view_count(self):
        """
        Sets the view_count parameter appropriately, using a 30-day average.
        """
        p = PageviewsClient().article_views("en.wikipedia", [self.concept.replace(' ', '_')])
        p = [p[key][self.concept.replace(' ', '_')] for key in p.keys()]
        p = int(sum([daily_view_count for daily_view_count in p if daily_view_count])/len(p))
        self.view_count = p

    def set_relevance(self, relevance):
        """
        :param relevance: Sets the concept's relevance parameter.
        """
        self.relevance = relevance


def conceptualize(user_input):
    """
    Attempts to map arbitrary textual input to a valid Concept. If the method is unsuccessful no Concept is
    returned. See also the similar `conceptmodel.model` static method, which binds arbitrary input to an entire
    ConceptModel instead.
    :param user_input: Arbitrary input, be it a name (e.g. Apple (company) -> Apple Inc.) or a text string (e.g.
    "the iPhone 5C, released this Thursday..." -> iPhone).
    """
    # Fetch the precise name of the node (article title) associated with the institution.
    raw_concepts = watsongraph.event_insight_lib.annotate_text(user_input)
    # If the correction call is successful, keep going.
    if 'annotations' in raw_concepts.keys() and len(raw_concepts['annotations']) != 0:
        matched_concept_node_label = raw_concepts['annotations'][0]['concept']['label']
        return matched_concept_node_label
