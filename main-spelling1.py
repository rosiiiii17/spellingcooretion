import streamlit as st

# ======================
# LOAD KAMUS (FIX: TANPA SPASI)
# ======================
with open("kbbi_dataset.txt", "r", encoding="utf-8") as f:
    kamus_txt = set([
        line.strip().lower()
        for line in f
        if " " not in line.strip()   # 🔥 penting: buang kata yang ada spasi
    ])


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
# SIMILARITY BONUS
# ======================
def similarity_bonus(a, b):
    return sum(1 for x, y in zip(a, b) if x == y)


# ======================
# FILTERING KAMUS
# ======================
def filtering_kamus(kata):
    return [k for k in kamus_txt if abs(len(k) - len(kata)) <= 2]


# ======================
# PREDIKSI DLD FINAL
# ======================
def prediksi_dld(kata):

    kata_asli = kata
    kata = kata.lower().strip(",.!?")

    # BENAR
    if kata in kamus_txt:
        return kata_asli, "BENAR", []

    # terlalu pendek
    if len(kata) <= 3:
        return kata_asli, "SKIP", []

    kandidat = filtering_kamus(kata)

    ranking = []

    for k in kandidat:
        jarak = damerau_levenshtein_distance(kata, k)
        bonus = similarity_bonus(kata, k)
        ranking.append((k, jarak, bonus))

    ranking.sort(key=lambda x: (x[1], abs(len(x[0]) - len(kata)), -x[2]))

    if len(ranking) == 0:
        return kata_asli, "TIDAK DIKOREKSI", []

    top3 = ranking[:3]

    kandidat_final, jarak, _ = top3[0]

    if jarak <= 2:
        return kandidat_final, "DLD", top3

    return kata_asli, "TIDAK DIKOREKSI", top3


# ======================
# UI STREAMLIT
# ======================
st.set_page_config(page_title="Skenario 1 - DLD", layout="centered")

st.title("📝 Spelling Correction - Skenario 1")
st.write("Metode: Damerau Levenshtein Distance (DLD)")

st.info("⚠️ Skenario 1 hanya untuk typo (tidak menangani spasi)")

teks = st.text_area("Masukkan kalimat:")

if st.button("Koreksi"):

    hasil_kalimat = []
    detail = []

    for kata in teks.split():

        pred, metode, top3 = prediksi_dld(kata)

        hasil_kalimat.append(pred)

        # 🔥 tampilkan SEMUA selain yang benar
        if metode != "BENAR":
            detail.append((kata, pred, metode, top3))

    hasil = " ".join(hasil_kalimat)

    st.subheader("✅ Hasil Perbaikan:")
    st.success(hasil)

    # ======================
    # DETAIL
    # ======================
    if detail:
        st.subheader("🔍 Detail Perbaikan:")

        for kata, pred, metode, top3 in detail:

            if metode == "TIDAK DIKOREKSI":
                st.write(f"⚠️ {kata} → ❌ tidak bisa dikoreksi")

            elif metode == "SKIP":
                st.write(f"⚠️ {kata} → (kata terlalu pendek, dilewati)")

            else:
                st.write(f"❌ {kata} → ✅ {pred} ({metode})")

            # tampilkan kandidat
            if top3:
                st.write("   🔎 Top Kandidat:")
                for i, (k, j, _) in enumerate(top3, start=1):
                    st.write(f"   {i}. {k} (jarak={j})")