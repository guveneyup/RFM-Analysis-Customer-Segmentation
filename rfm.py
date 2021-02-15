import pandas as pd
import datetime as dt


pd.set_option("display.max_columns", None)
df_ = pd.read_excel("C:/Users/EyupcanGuven/Desktop/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")
df = df_.copy()

df.head()
df.tail()
df.shape
df.info()
df.isnull().sum()


# Eşsiz ürün sayısı nedir?
df["Description"].nunique()

# hangi urunden kacar tane var?
df["Description"].value_counts().head()

# en cok siparis edilen urun hangisi?
df.groupby("Description").agg({"Quantity": "sum"}).head()

# yukarıdaki çıktıyı nasil siralariz?
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# toplam kac fatura kesilmiştir?
df["Invoice"].nunique()

# Eksik gözlem değerlerini silelim
df.dropna(inplace=True)
# iadeleri çıkartıp yeniden df oluşturalım
df = df[~df["Invoice"].str.contains("C", na=False)]
# Urun iadesi olmayanları atama yapalım
df = df[df["Quantity"] > 0]
#  Ürün adedi ile ürün fiyatlarını çarpıp TotalPrice ismiyle yeni değişken oluşturmak
df["Total_price"] = df["Quantity"] * df["Price"]

# En son işlem yapılan tarih
df["InvoiceDate"].max()


today_date = dt.datetime(2011, 12, 11)

# Recency, Frequence ve Monetary değişkenlerini oluşturalım
rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days,
                                     "Invoice": lambda num: num.nunique(),
                                     "Total_price": lambda Total_price: Total_price.sum()})


# Oluşturulan yeni değişkenleri isimlendirelim
rfm.columns = ["Recency", "Frequency", "Monitary"]


# Monetary değişkeninin içinde yer alan gözlemlerin sıfırdan büyük olanlarını alalım
rfm = rfm[(rfm["Monitary"] > 0)]

# Recency, Frequence ve Monetary değişkenlerini skorlara ayıralım
rfm["recency_score"] = pd.qcut(rfm.Recency, 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monitary_score"] = pd.qcut(rfm.Monitary, 5, labels=[1, 2, 3, 4, 5])


# Skorlamaları tek bir değişkende birleştirip yeni RFM_SCORE isimli değişken oluşturalım
rfm["rfm_score"] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str) +
                    rfm["monitary_score"].astype(str))

# Segment işlemleri
seg_map = {
    r"[1-2][1-2]": "Hibernating",
    r"[1-2][3-4]": "At_Risk",
    r"[1-2]5": "Cant_Lose_Them",
    r"3[1-2]": "About_to_Sleep",
    r"33": "Need_Attention",
    r"[3-4][4-5]": "Loyal_Customer",
    r"41": "Promising",
    r"[4-5][2-3]": "Potential_Loyalists",
    r"51": "New_Customer",
    r"5[4-5]": "Champions"
}

rfm['Segment'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str)

rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)
rfm[["Segment", "Recency", "Frequency", "Monitary"]].groupby("Segment").agg(
    ["mean", "count", "median"])


# Loyal_Customers segmentinde bulunan kişileri, tüm kişileri ve Segment kırılımında her bir değişken öbeğindeki
# mean ve count değerlerini csv formatında excel'e aktaralım.
new_df = pd.DataFrame()

new_df["Loyal_Customers"] = rfm[rfm["Segment"] == "Loyal_Customers"].index

new_df.to_csv("Loyal_Customers.csv")
rfm.to_csv("rfm.csv")

group = rfm[["Segment", "Recency", "Frequency", "Monitary"]].groupby("Segment").agg(
    ["mean", "count", "median"])


group.to_csv("groupp_agg.csv")

