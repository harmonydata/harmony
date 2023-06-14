import spacy

nlp = spacy.blank("en")


def get_change_en(doc) -> dict:
    """
    Identify how to change an English sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for tok in doc:
        if tok.text.lower() in {"always", "rather", "really", "very", "totally", "utterly", "absolutely", "completely",
                                "frequently", "often", "sometimes", "generally", "usually"}:
            return {tok.i: ("replace", "never")}
        if tok.text.lower() in {"never", "not", "n't"}:
            return {tok.i: ("replace", "")}
        if tok.text.lower() in {"cannot"}:
            return {tok.i: ("replace", "can")}
    result = {}
    for tok in doc:
        if tok.text.lower() in {"is", "are", "am", "are", "was", "were", "has", "have", "had"}:
            result[tok.i] = "insert_after", "not"
    if len(result) > 0:
        return result
    #     print ("fallback", doc)
    return {0: ("insert_before", "never")}


def get_change_pt(doc) -> dict:
    """
    Identify how to change a Portuguese sentence from positive to negative or vice versa.
    :param doc:
    :return:
    """
    for tok in doc:
        if tok.text.lower() in {"sempre", "bastante", "realmente", "muito", "totalmente", "totalmente", "absolutamente",
                                "completamente",
                                "frequentemente", "frequentemente", "vezes", "geralmente", "geralmente"}:
            return {tok.i: ("replace", "nunca")}
        if tok.text.lower() in {"nunca", "jamais", "nem", "não"}:
            return {tok.i: ("replace", "")}
    result = {}
    if len(result) > 0:
        return result
    return {0: ("insert_before", "não")}


def negate(text: str, language: str) -> str:
    """
    Converts negative sentences to pos and vice versa.
    Not meant to generate 100% accurate natural language, it's to go into transformer model and is not shown to a human.
    :param text:
    :param language: "en" or "pt"
    :return: the sentence negated
    """
    doc = nlp(text)

    if language == "pt":
        changes = get_change_pt(doc)
    else:
        changes = get_change_en(doc)

    text = ""
    for tok in doc:
        this_token_text = tok.text
        if tok.i in changes:
            change_operation, change_text = changes[tok.i]
            if change_operation == "replace":
                this_token_text = change_text
            elif change_operation == "insert_after":
                this_token_text += " " + change_text
            elif change_operation == "insert_before":
                this_token_text = change_text + " " + this_token_text
        text += this_token_text + tok.whitespace_
    return text