    def term_matches(text, field_name, term):
        """ Counts the number of occurences of term and its variants in text

        """
        forms_list = term_forms[field_name].get(term, [term])
        options = term_analysis[field_name]
        token_mode = options.get('token_mode', tm_tokens)
        case_sensitive = options.get('case_sensitive', False)
        first_term = forms_list[0]
        if token_mode == tm_full_term:
            return full_term_match(text, first_term, case_sensitive)
        else:
            # In token_mode='all' we will match full terms using equals and
            # tokens using contains
            if token_mode == tm_all and len(forms_list) == 1:
                pattern = re.compile(r'^.+\b.+$', re.U)
                if re.match(pattern, first_term):
                    return full_term_match(text, first_term, case_sensitive)
            return term_matches_tokens(text, forms_list, case_sensitive)


    def full_term_match(text, full_term, case_sensitive):
        """Counts the match for full terms according to the case_sensitive
              option

        """
        if not case_sensitive:
            text = text.lower()
            full_term = full_term.lower()
        return 1 if text == full_term else 0

    def get_tokens_flags(case_sensitive):
        """Returns flags for regular expression matching depending on text
              analysis options

        """
        flags = re.U
        if not case_sensitive:
            flags = (re.I | flags)
        return flags


    def term_matches_tokens(text, forms_list, case_sensitive):
        """ Counts the number of occurrences of the words in forms_list in
               the text

        """
        flags = get_tokens_flags(case_sensitive)
        expression = r'(\b|_)%s(\b|_)' % '(\\b|_)|(\\b|_)'.join(forms_list)
        pattern = re.compile(expression, flags=flags)
        matches = re.findall(pattern, text)
        return len(matches)
