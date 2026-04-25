import streamlit as st

# ======================
# LOAD KAMUS
# ======================
with open("kbbi_dataset.txt", "r", encoding="utf-8") as f:
    kamus_txt = set([line.strip() for line in f])


# ======================
# DLD FUNCTION
# ======================
def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)

    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,
                d[(i, j - 1)] + 1,
                d[(i - 1, j - 1)] + cost,
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)

    return d[lenstr1 - 1, lenstr2 - 1]


# ======================
# FILTERING KANDIDAT
# ======================
def filtering_kamus(kata):
    kandidat = []

    for k in kamus_txt:
        if abs(len(k) - len(kata)) > 2:
            continue
        if k[0] != kata[0]:
            continue

        kandidat.append(k)

        if len(kandidat) >= 10:
            break

    return kandidat


# ======================
# PREDIKSI DLD ONLY
# ======================
def prediksi_dld(kata):

    # kalau sudah benar
    if kata in kamus_txt:
        return kata, "BENAR"

    kandidat = filtering_kamus(kata)

    ranking = []

    for k in kandidat:
        jarak = damerau_levenshtein_distance(kata, k)
        ranking.append((k, jarak))

    ranking.sort(key=lambda x: x[1])

    if len(ranking) > 0:
        return ranking[0][0], "DLD"

    return kata, "TIDAK DIKETAHUI"


# ======================
# UI STREAMLIT
# ======================
st.set_page_config(page_title="Skenario 1 - DLD", layout="centered")

st.title("📝 Spelling Correction - Skenario 1")
st.write("Metode: Damerau Levenshtein Distance (DLD)")

teks = st.text_area("Masukkan kalimat:")

if st.button("Koreksi"):

    hasil_kalimat = []
    detail = []

    for kata in teks.split():

        pred, metode = prediksi_dld(kata)

        hasil_kalimat.append(pred)

        if pred != kata:
            detail.append((kata, pred, metode))

    hasil = " ".join(hasil_kalimat)

    st.subheader("✅ Hasil Perbaikan:")
    st.success(hasil)

    if detail:
        st.subheader("🔍 Detail Perbaikan:")
        for d in detail:
            st.write(f"❌ {d[0]} → ✅ {d[1]} ({d[2]})")