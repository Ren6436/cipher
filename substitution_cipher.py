import numpy as np
import random
from math import log
from string import ascii_uppercase

alphabet = ascii_uppercase + "_"


def substitute_encrypt(plaintext, key):
    mapping = {alphabet[i]: key[i] for i in range(len(alphabet))}
    return ''.join([mapping.get(c.upper(), c) for c in plaintext])


def substitute_decrypt(ciphertext, key):
    reverse_mapping = {key[i]: alphabet[i] for i in range(len(alphabet))}
    return ''.join([reverse_mapping.get(c.upper(), c) for c in ciphertext])


def get_bigrams(text):
    return [text[i:i + 2] for i in range(len(text) - 1)]


def transition_matrix(bigrams):
    n = len(alphabet)
    char_to_idx = {char: i for i, char in enumerate(alphabet)}
    tm = np.ones((n, n))

    for bigram in bigrams:
        if len(bigram) == 2:
            c1, c2 = bigram
            if c1 in char_to_idx and c2 in char_to_idx:
                i = char_to_idx[c1]
                j = char_to_idx[c2]
                tm[i][j] += 1

    tm /= tm.sum()
    return tm


def plausibility(text, TM_ref):
    bigrams_obs = get_bigrams(text)
    TM_obs = transition_matrix(bigrams_obs)
    return np.sum(TM_obs * np.log(TM_ref))


def prolom_substitute(text, TM_ref, iter, start_key=None):
    if start_key is None:
        current_key = list(alphabet)
        random.shuffle(current_key)
        current_key = ''.join(current_key)
    else:
        current_key = start_key

    decrypted_current = substitute_decrypt(text, current_key)
    p_current = plausibility(decrypted_current, TM_ref)

    for i in range(1, iter + 1):
        candidate_key = list(current_key)
        i1, i2 = random.sample(range(len(alphabet)), 2)
        candidate_key[i1], candidate_key[i2] = candidate_key[i2], candidate_key[i1]
        candidate_key = ''.join(candidate_key)

        decrypted_candidate = substitute_decrypt(text, candidate_key)
        p_candidate = plausibility(decrypted_candidate, TM_ref)

        q = p_candidate / p_current if p_current != 0 else 0

        if q > 1 or random.random() < 0.01:
            current_key = candidate_key
            p_current = p_candidate
            decrypted_current = decrypted_candidate

        if i % 50 == 0:
            print(f"Iteration {i}, log plausibility: {p_current:.2f}")

    return current_key, decrypted_current, p_current