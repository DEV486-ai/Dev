// পণ্যের কার্ড বসানো
const grid = document.getElementById("product-grid");
const select = document.getElementById("product-select");

PRODUCTS.forEach((p) => {
  const card = document.createElement("article");
  card.className = "product-card";
  card.innerHTML = `
    ${p.tag ? `<span class="tag">${p.tag}</span>` : ""}
    <h3>${p.name}</h3>
    <p class="product-en">${p.nameEn}</p>
    <p class="product-desc">${p.desc}</p>
    <div class="product-foot">
      <span class="price">৳${p.price} <small>/ ${p.unit}</small></span>
      <a href="#order" class="btn btn-small">অর্ডার করুন</a>
    </div>
  `;
  card.querySelector(".btn-small").addEventListener("click", () => {
    select.value = p.name;
  });
  grid.appendChild(card);

  const opt = document.createElement("option");
  opt.value = p.name;
  opt.textContent = p.name;
  select.appendChild(opt);
});

// অর্ডার ফর্ম সাবমিশন
const form = document.getElementById("order-form");
const flashBox = document.getElementById("flash-box");

function showFlash(message, ok) {
  flashBox.textContent = message;
  flashBox.hidden = false;
  flashBox.className = "flash " + (ok ? "flash-success" : "flash-error");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());

  try {
    const res = await fetch("/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!res.ok) throw new Error("server error");
    const result = await res.json();
    showFlash(result.message, true);
    form.reset();
  } catch (err) {
    // app.py ছাড়া (শুধু স্ট্যাটিক হোস্টিং) চললে ব্যাকএন্ড থাকবে না, তাই এই বার্তা দেখাবে
    showFlash("দুঃখিত, অর্ডার সিস্টেম এখন চালু নেই। সরাসরি ফোনে যোগাযোগ করুন।", false);
  }
});
