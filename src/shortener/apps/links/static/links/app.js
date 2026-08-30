document.addEventListener("DOMContentLoaded", () => {
    const copyBtn = document.getElementById("copy-btn")
    if (!copyBtn) return

    copyBtn.addEventListener("click", async () => {
        const link = document.getElementById("result-link").textContent
        await navigator.clipboard.writeText(link)
        copyBtn.textContent = "Copied"
        setTimeout(() => { copyBtn.textContent = "Copy"}, 2000)
    })
})