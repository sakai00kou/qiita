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
    const uploadForm = document.querySelector("#upload-form");
    const avatar = document.querySelector("#avatar");
    const chosenFile = document.querySelector("#chosen-file");
    const submitButton = document.querySelector("#submit");
    const zipCheck = document.querySelector("#zip");

    // 選択済みファイルリストエリアの未選択時状態の保持
    const noFileChosen = chosenFile.firstChild;



    /**
     * Initialize webpage elements
     * ウェブページの初期化
     */
    // アップロード/ダウンロード共通のページ初期化
    await initializeCommons();

    // アップロード関連情報の取得
    let targetInfo = await getTransferTargetInfo("/api/upload");

    if (!targetInfo || targetInfo === null) {
        console.error ("[Token Error] Failed to get token.");
    }

    // アップロード関連情報の設定
    if(targetInfo) {
        // バケット名、フォルダー名
        document.querySelector("#bucket").textContent += targetInfo["bucket"];
        document.querySelector("#folder").textContent += targetInfo["prefix"];
    }



    /**
     * Clear the file chosen area
     * 選択済みファイルリストエリアのクリア
     */
    const clearChosenFile = () => {
        avatar.value = "";

        while (chosenFile.firstChild) {
            chosenFile.removeChild(chosenFile.firstChild);
        }
        chosenFile.appendChild(noFileChosen);

        zipCheck.checked = false;
    };


    /**
     * Upload file chosen event
     * ファイル選択イベント
     */
    avatar.addEventListener("change", (event) => {

        // ファイルが選択された場合、選択済みファイルリストエリアに表示
        if (0 < event.target.files.length) {
            while (chosenFile.firstChild) {
                chosenFile.removeChild(chosenFile.firstChild);
            }

            const ol = document.createElement("ol");

            for (const file of event.target.files) {
                const li = document.createElement("li");
                li.textContent = `${file.name} | ${new Intl.NumberFormat('ja-JP').format(file.size)} Bytes`;
                ol.appendChild(li);
            }

            chosenFile.appendChild(ol);
        } else {
            clearChosenFile();
        }

        submitButton.disabled = (avatar.files.length === 0);
    });


    /**
     * Submit button click event
     * サブミットボタンクリック時イベント
     */
    uploadForm.addEventListener("submit", async (e) => {
        // 通常のサブミットイベントの停止
        e.preventDefault();

        // コントロールエレメントを非活性化
        lockControlElements(true);

        const formData = new FormData();
        const out_resultObj = {};

        let compMsg, errorMsg;

        try{
            // アップロードに必要なフォームデータの設定
            const fields = targetInfo["contents"]["fields"];
            Object.keys(fields).forEach(key => formData.append(key, fields[key]));


            // 署名付き URL
            const presignedUrl = targetInfo["contents"]["url"];

            if (zipCheck.checked) {
                // [Create Zip] チェックボックスがチェックされている場合、ファイルをZIPにまとめてアップロード

                const zip = new JSZip();

                // 一時的にバイナリーデータバッファーとしてファイルをZIPにまとめる
                for (const file of avatar.files) {
                    const arrayBuffer = await new Response(file).arrayBuffer();
                    zip.file(file.name, arrayBuffer);
                }

                const zipBlob = await zip.generateAsync({ type: "blob" });
                const zipFile = `archive-${Date.now()}.zip`

                formData.append("file", zipBlob, zipFile);

                // アップロード
                await uploadFile(formData, presignedUrl, zipFile, out_resultObj);
            } else {
                // [Create Zip] チェックボックスがチェックされていない場合、ファイルを連続でアップロード

                const subFolder = `/subfolder-${Date.now()}/`;

                formData.set("key", formData.get("key").replace("/", subFolder));

                for (const file of avatar.files) {
                    formData.append("file", file, file.name);
                    await uploadFile(formData, presignedUrl, file.name, out_resultObj);
                    formData.delete("file");
                }
            }

            // アップロード処理結果メッセージの生成
            compMsg = JSON.stringify(out_resultObj, null, " ").replace(/{|}|"|,/g,"");

        } catch (error) {
            errorMsg = error;
            console.error(error);
        } finally {
            // 処理結果のダイアログ表示
            const endMsg = compMsg || errorMsg;
            alert(`Upload process finished.\n${endMsg}`);

            clearChosenFile();
            lockControlElements(false);
        }
    });


    /**
     * Upload file
     * ファイルのアップロード
     * @param {FormData} formData アップロードのためのフォームパラメータ
     * @param {String} presignedUrl 署名付き URL (POST)
     * @param {String} fileName アップロードファイル名
     * @param {Array} out_resultObj アップロード成否
     */
    const uploadFile = async (formData, presignedUrl, fileName, out_resultObj) => {
        out_resultObj[fileName] = "NG";

        const params = {
            method: "POST",
            body: formData
        };

        try {
            // アップロード
            const response = await fetch(presignedUrl, params);

            if(!response.ok) {
                throw new Error(`Fetch Call response failed status: ${response.status}, ${response.statusText}`);
            }

            out_resultObj[fileName] = "OK";
        } catch (error) {
            throw new Error(`[Upload] ${error}, ${fileName}`);
        }
    }
});
