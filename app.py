import os

import streamlit as st
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MultiLabelBinarizer
from whoosh.index import open_dir

from indexer import create_index
from search import search_index, document_label, split_data_label

# Pilih aksi
option = st.sidebar.selectbox("Pilih Aksi",
                              ["Index Dokumen", "Cari Dokumen", "Klasifikasi Dokumen", "Informasi Kelas Dokumen"])

# Jalur direktori
dokumen_dir = "dokumen"
index_dir = "indexer"

if option == "Index Dokumen":
    st.header("Indexing Dokumen")
    if st.button("Mulai Indexing"):
        if not os.path.exists(dokumen_dir):
            st.error("Folder dokumen tidak ditemukan.")
        else:
            create_index(index_dir)
            st.success("Indexing selesai.")
elif option == "Cari Dokumen":
    st.title("Aplikasi Pencarian Dokumen")
    st.header("Pencarian")
    query = st.text_input("Masukkan kata kunci")
    if st.button("Cari"):
        if not os.path.exists(index_dir):
            st.error("Index belum dibuat. Silakan lakukan indexing terlebih dahulu.")
        elif not query:
            st.warning("Silakan masukkan kata kunci.")
        else:
            results = search_index(index_dir, query)
            st.write(f"Hasil ditemukan: {len(results)} dokumen")
            for r in results:
                st.write("------")
                st.write(f"ID Dokumen: {r['doc_id']}")
                st.write(f"Kategori Dokumen: {r['topics']}")
                st.write(f"Skor: {r['score']:.4f}")
                st.write(r['title'][:500])
elif option == "Klasifikasi Dokumen":
    st.header("Klasifikasi Dokumen")
    content = st.text_input("Masukkan Isi kontenmu dulu lah")
    if content is None:
        st.warning("Isian tidak boleh kosong !!! ")
    else:
        if st.button("Indeks Lagi"):
            if not content.strip():
                st.warning("Isian tidak boleh kosong!")
            else:
                try:
                    ix = open_dir(index_dir)
                    writer = ix.writer()
                    writer.add_document(title=content)
                    writer.commit()
                    st.success("Konten berhasil ditambahkan ke indeks.")
                except Exception as e:
                    st.error(f"Gagal menambahkan ke indeks: {e}")

elif option == "Informasi Kelas Dokumen":
    st.write("Informasi Kelas Dokumen")
    categories = document_label()

    for i in categories:
        st.write(i)

    df = split_data_label()
    st.header("DATASET ROUTERS")
    st.write(df)

    tfidf = TfidfVectorizer(stop_words=stopwords.words('english'), max_features=5000)
    X = tfidf.fit_transform(df['text'])
    st.header("X FEATURE")
    st.write(X)

    st.write("Encode Label")
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(df['labels'])  # y = array (n_samples, n_labels)

    st.write("Split 80% training dan 20% test")
    X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=0.2)

    st.header("DATA X TRAIN")
    st.write(X_train)

    st.header("Data Y TRAIN")
    st.write(Y_train)

    model = OneVsRestClassifier(MultinomialNB())
    model.fit(X_train, Y_train)
    y_pred = model.predict(X_test)

    st.header("HASIL PREDIKSI")
    st.write(y_pred)

    st.header("Skor Akurasi")
    st.write(accuracy_score(Y_test, y_pred))

    st.header("Matrix Confusion")
    st.write(classification_report(Y_test, y_pred, target_names=mlb.classes_))
