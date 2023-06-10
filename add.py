@app.route('/add-recommendation', methods=['GET'])
def add_recomendation():

    # Load the startup features from Firestore
    startup_features_ref = db.collection('startup')
    startup_features_docs = startup_features_ref.stream()

    startup_features = []
    startup_ids = []
    for doc in startup_features_docs:
        data = doc.to_dict()
        startup_features.append(data['tingkat_perkembangan_perusahaan'] + ' ' + data['industri_startup'])
        startup_ids.append(str(doc.id))

    # Load the investor features from Firestore
    investor_features_ref = db.collection('investor_loker')
    investor_features_docs = investor_features_ref.stream()

    investor_features = []
    investor_ids = []
    for doc in investor_features_docs:
        data = doc.to_dict()
        investor_features.append(data['target_perkembangan'] + ' ' + data['target_industri'])
        investor_ids.append(doc.id)

    # Preprocess the data using Tokenizer
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(startup_features + investor_features)
    startup_sequences = tokenizer.texts_to_sequences(startup_features)
    startup_padded = pad_sequences(startup_sequences)

    investor_sequences = tokenizer.texts_to_sequences(investor_features)
    investor_padded = pad_sequences(investor_sequences)

    # Convert padded sequences to tensors
    startup_tensors = tf.convert_to_tensor(startup_padded, dtype=tf.float32)
    investor_tensors = tf.convert_to_tensor(investor_padded, dtype=tf.float32)

    # Calculate cosine similarity between startup and investor tensors
    similarity_matrix = cosine_similarity(startup_tensors, investor_tensors)

    def get_investor_matches(startup_id):
        matches = {}
        startup_index = startup_ids.index(startup_id)
        similarities = similarity_matrix[startup_index]
        sorted_indexes = np.argsort(similarities)[::-1]
        top_matches = [investor_ids[i] for i in sorted_indexes[:20]]
        matches[startup_id] = top_matches
        return matches

    # Add investor matches to Firestore collection
    def add_investor_matches(startup_id, investor_matches):
        matches_ref = db.collection('investor_matches')
        matches_ref.document(startup_id).set({ 'investor_matches': investor_matches })
    
    #perform the matching and add matches for each startup
    result={}
    for id in startup_ids:
        input_id = id
        investor_matches = get_investor_matches(input_id)
        add_investor_matches(input_id, investor_matches[input_id])  

    return jsonify(result)
    