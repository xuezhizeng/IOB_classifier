import numpy as np


def get_vectors(all_sentences, word_2_vec):
    random_vec = np.mean(np.vstack(word_2_vec.values()).astype('float'), axis=0)
    all_OOV_words = []
    all_sentences_vecs = []    
    for sentence in all_sentences:
        sentence_vecs = []
        for word in sentence:
            if word not in word_2_vec.keys():
                if word in ['a', 'an', 'to', 'of', 'and']:
                    vec = word_2_vec['from']
                else:
                    vec = random_vec
                    all_OOV_words.append(word)
            else:
                vec = word_2_vec[word]
            sentence_vecs.append(vec)
        sentence_vecs = np.vstack(sentence_vecs).astype('float')
        sentence_vecs = sentence_vecs[np.newaxis]
        all_sentences_vecs.append(sentence_vecs)
    all_sentences_vecs = np.concatenate(all_sentences_vecs, axis=0)
    return all_sentences_vecs, all_OOV_words


def load_data():
    word_2_vec = {}
    with open('wordvecs.txt') as f:
        for line in f:
            
            line = line.split()
            word = line[0]
            vec = line[1:]
            word_2_vec[word] = vec    
    all_sentences = []
    all_targets = []
    is_end_of_a_sentence = False
    sentence = []         
    sentence_labels = []  
    with open('news_tagged_data.txt') as f:
        for line in f:
            if line == '\n':  
                is_end_of_a_sentence = True
            if is_end_of_a_sentence:
                all_sentences.append(sentence)
                all_targets.append(sentence_labels)
                sentence = []
                sentence_labels = []
                is_end_of_a_sentence = False
            else:
                line = line.strip()
                line = line.lower()
                line = line.split()
                word = line[0]
                word_label = line[1]
                sentence.append(word)
                sentence_labels.append(word_label)
    
    longest_len = max([len(s) for s in all_sentences])
    list_of_all_targets = []
    for targets in all_targets:
        list_of_all_targets.extend(targets) 
    
    total_number_of_classes = len(set(list_of_all_targets))
    target_to_index = {}
    set_of_all_targets = set(list_of_all_targets)

    for index,target in enumerate(set_of_all_targets):
        target_to_index[target] = index

    index_to_target = {}    
    
    for index, target in enumerate(set_of_all_targets):
        index_to_target[index] = target

    all_padded_sentences = []
    all_padded_targets = []
    all_masks = []

    for sentence, target in zip(all_sentences, all_targets):
        length = len(sentence)
        to_pad = longest_len - length
        padding = ['reyhan'] * to_pad
        sentence = sentence + padding
        mask = np.ones(longest_len)
        if to_pad != 0:
            mask[-to_pad:] = np.zeros(to_pad)
        target = [target_to_index[t] for t in target]
        target = target + list(np.zeros(to_pad))
        all_padded_sentences.append(sentence)
        all_masks.append(mask)
        onehot = np.zeros((len(target), 9))
        onehot[range(29), target] = 1
        all_padded_targets.append(onehot[np.newaxis])

    
    word_2_vec['reyhan'] = np.zeros(300)
    all_sentences_vecs, all_OOV_words = get_vectors(all_padded_sentences, word_2_vec)
    all_masks = np.vstack(all_masks)
    all_padded_targets = np.concatenate(all_padded_targets, axis=0)
    return all_sentences_vecs, all_masks, all_padded_targets, word_2_vec, index_to_target