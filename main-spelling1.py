import streamlit as st

# ======================
# LOAD KAMUS (TANPA SPASI)
# ======================
with open("kbbi_dataset.txt", "r", encoding="utf-8") as f:
    kamus_txt = set([
        line.strip().lower()
        for line in f
        if " " not in line.strip()
    ])


# ======================
# DLD
# ======================
def damerau_levenshtein_distance(s1, s2):
    d = {}
    for i in range(-1, len(s1)+1):
        d[(i, -1)] = i+1
    for j in range(-1, len(s2)+1):
        d[(-1, j)] = j+1

    for i in range(len(s1)):
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i-1, j)] + 1,
                d[(i, j-1)] + 1,
                d[(i-1, j-1)] + cost
            )
            if i and j and s1[i] == s2[j-1] and s1[i-1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i-2, j-2)] + cost)

    return d[len(s1)-1, len(s2)-1]


# ======================
# FILTER KANDIDAT
# ======================
def filtering_kamus(kata):
    return [k for k in kamus_txt if abs(len(k) - len(kata)) <= 2]


# ======================
# MODEL SKENARIO 1 (DLD ONLY)
# ======================
def model_skenario1(kata):

    kata = kata.lower().strip(",.!?")

    # 1. kata benar
    if kata in kamus_txt:
        return kata, "BENAR", []

    # 2. kandidat
    kandidat = filtering_kamus(kata)

    ranking = []
    for k in kandidat:
        jarak = damerau_levenshtein_distance(kata, k)
        ranking.append((k, jarak))

    ranking.sort(key=lambda x: x[1])

    if ranking:
        top3 = ranking[:3]
        kandidat_terbaik, jarak = ranking[0]

        # hanya koreksi typo ringan
        if jarak <= 2:
            return kandidat_terbaik, "DLD", top3

        return kata, "TIDAK DIKOREKSI", top3

    return kata, "TIDAK DIKOREKSI", []


# ======================
# UI
# ======================
st.title("Spelling Correction - Skenario 1")
st.write("Metode: DLD")

teks = st.text_area("Masukkan kalimat:")

if st.button("Koreksi"):

    hasil_kalimat = []
    detail = []

    for kata in teks.split():

        hasil, metode, top3 = model_skenario1(kata)

        hasil_kalimat.append(hasil)

        if metode != "BENAR":
            detail.append((kata, hasil, metode, top3))

    st.subheader("Hasil:")
    st.success(" ".join(hasil_kalimat))

    st.subheader("Detail:")

    for kata, hasil, metode, top3 in detail:

        if metode == "TIDAK DIKOREKSI":
            st.write(f"⚠️ {kata} → tidak bisa dikoreksi")

        else:
            st.write(f"❌ {kata} → {hasil} ({metode})")

        if top3:
            st.write("Top Kandidat:")
            for i, (k, j) in enumerate(top3, 1):
                st.write(f"{i}. {k} (jarak={j})")