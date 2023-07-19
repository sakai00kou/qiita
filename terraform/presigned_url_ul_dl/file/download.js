/**
 * Import module
 * モジュールの読み込み
 */
// アップロード/ダウンロード共有ファイル
import { initializeCommons, getTransferTargetInfo, lockControlElements } 
    from "./ul-dl-shared.js";



/**
 * DOM Content Loaded event
 * DOMコンテントロード後イベント
 */
window.addEventListener("DOMContentLoaded", async () => {

    // ウェブページエレメント
    const submitButton = document.querySelector("#submit");
    const allCheck = document.querySelector("#check-all");
    const zipCheck = document.querySelector("#zip");



    /**
     * Initialize webpage elements
     * ウェブページの初期化
     */
    // アップロード/ダウンロード共通のページ初期化
    await initializeCommons();

    // ダウンロード関連情報の取得
    let targetInfo = await getTransferTargetInfo("/api/download");

    if (!targetInfo || targetInfo === null) {
        console.error ("[Token Error] Failed to get token.");
    }

    // ダウンロード関連情報の設定
    if(targetInfo){
        // バケット名、フォルダー名
        document.querySelector("#bucket").textContent += targetInfo["bucket"];
        document.querySelector("#folder").textContent += targetInfo["prefix"];

        // ダウンロードファイル一覧の生成
        const fileTableBody = document.querySelector("#file-table > tbody");
        const targetContents = targetInfo["contents"] || [];

        targetContents.forEach((info) => {
            const row = fileTableBody.insertRow(-1);

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.name = "selected-file";
            checkbox.value = info["presignedUrl"];
            checkbox.addEventListener("change", () => {
                submitButton.disabled = !getAllFileCheckboxes().some(checkbox => checkbox.checked);
            });
            row.insertCell(-1).appendChild(checkbox);

            const anchor = document.createElement("a");
            anchor.href = info["presignedUrl"];
            anchor.textContent = info["name"];
            row.insertCell(-1).appendChild(anchor);

            row.insertCell(-1).textContent = `${info["size"]} Bytes`;
            row.insertCell(-1).textContent = info["lastModified"];
        });
    }



    /**
     * Submit button click event
     * サブミットボタンクリック時イベント
     */
    submitButton.addEventListener("click", async () => {
        // チェックされている全てのファイルのURLを取得
        const checkedFileUrls = getAllFileCheckboxes().filter(cb => cb.checked).map(cb => cb.value);

        // コントロールエレメントを非活性化
        lockControlElements(true);

        try {
            if (zipCheck.checked) {
                // [Create Zip] チェックボックスがチェックされている場合、ファイルをZIPにまとめてダウンロード

                // JSZip オブジェクト
                const zip = new JSZip();

                // 一時的にバイナリーデータとしてダウンロードしたファイルをZIPにまとめる
                const fetchPromises = checkedFileUrls.map(async (url) => {
                    let response = await downloadFile(url);

                    if(response.ok) {
                        const blob = response.blob;

                        const arrayBuffer = await new Response(blob).arrayBuffer();
                        const filename = url.split("?")[0].split("/").pop();

                        zip.file(filename, arrayBuffer);
                    }
                });

                try {
                    await Promise.all(fetchPromises);

                    // ZIP のバイナリオブジェクト
                    const zipBlob = await zip.generateAsync({ type: "blob" });

                    // リンクを生成して、ZIP ファイルをダウンロード
                    const anchor = document.createElement("a");
                    anchor.href = URL.createObjectURL(zipBlob);
                    anchor.download = `${targetInfo["prefix"].slice(0, -1)}-${Date.now()}.zip`;
                    anchor.click();
                    URL.revokeObjectURL(anchor.href);
                } catch (error) {
                    console.error(`[ZIP Error] ${error}`);
                }
            } else {
                // [Create Zip] チェックボックスがチェックされていない場合、ファイルを連続でダウンロード

                const fetchPromises = checkedFileUrls.map(async (url) => {
                    // 一時的にバイナリオブジェクトとしてダウンロード
                    let response = await downloadFile(url);

                    if(response.ok) {
                        // リンクを生成して、そのままのファイルをダウンロード
                        const anchor = document.createElement("a");
                        anchor.href = URL.createObjectURL(response.blob);
                        anchor.download = url.split("?")[0].split("/").pop();
                        anchor.click();
                        URL.revokeObjectURL(anchor.href);
                    }
                });

                await Promise.all(fetchPromises);
            }
        } catch (error) {
            console.error(error);
        } finally {
            // コントロールエレメントを活性化
            lockControlElements(false);
        }
    });


    /**
     * dowload file
     * ファイルのダウンロード
     * @param {String} presignedUrl 署名付き URL (GET)
     * @returns {Object} blob: バイナリダウンロードデータ, ok: ダウンロード成否
     */
    const downloadFile = async (presignedUrl) => {
        let response;

        try {
            // ダウンロード
            response = await fetch(presignedUrl);

            if (!response.ok) {
                console.log(`Fetch Call response failed status: ${response.status}, ${response.statusText}`);
            }
        } catch (error) {
            throw new Error(`[Download] ${error}, ${presignedUrl}`);
        }

        return { blob: await response.blob(), ok: response.ok };
    }


    /**
     * All download checkboxes change event
     * 全ダウンロードチェックボックスのチェック時イベント 
    */
    allCheck.addEventListener("change", () => {
        getAllFileCheckboxes().forEach((checkbox) => {
            checkbox.checked = allCheck.checked;
        });

        submitButton.disabled = !allCheck.checked;
    });


    /**
     * Get all download checkboxes
     * 全てのダウンロードのチェックボックスエレメントを取得
     * @return {Node} 全てのダウンロードのチェックボックスエレメント
    */
    const getAllFileCheckboxes = () => {
        return Array.from(document.querySelectorAll("input[name=selected-file]"));
    }
});
