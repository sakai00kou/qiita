/**
 * Import module
 * モジュールの読み込み
 */
// 環境変数
import { USERPOOL_DOMAIN, USERPOOL_REGION, USERPOOL_CLIENT_ID, EXECUTE_API_STAGE }
    from "./env-vals.js";



/**
 * Environment valiables
 * 環境変数
 */
const domain = USERPOOL_DOMAIN;
const region = USERPOOL_REGION;
const clientId = USERPOOL_CLIENT_ID;



/**
 * HTTPリクエスト実行 (Fetch API のラッパー)
 * @param {String} uri リクエストURI
 * @param {Object} params {name: value} リクエストパラメータ
 * @return {Object} レスポンスオブジェクト
 */
const fetchWrapper = async (uri, params) => {
    let data;
    let response;

    try {
        response = await fetch(uri, params);
        data = await response.json();
    } catch (error) {
        throw new Error(`Fetch Call response failed] status: ${response.status}`);
    }

    return data;
}



/**
 * Get signed URL and related information for upload/download
 * アップロード/ダウンロードのための署名付きURLと関連情報の取得
 * @param {string} resourcePath 呼び出すAPIのリソースパス情報
 * @returns {object} 署名付きURLと関連情報
*/
export const getTransferTargetInfo = async (resourcePath) => {
    let idToken = sessionStorage.getItem("id_token");

    // トークンがセッション情報から取得できなかった場合は処理終了
    if (idToken === null) {
        throw new Error("[Token Error] Failed to get token.");
    }

    /** アップロード/ダウンロードのための関連情報 */
    let targetInfo;

    try{
        let apiStage = EXECUTE_API_STAGE;

        // API 呼び出し実行
        targetInfo = await fetchWrapper(`${location.origin}${apiStage}${resourcePath}`, 
                                        {
                                            method: "GET",
                                            headers: {
                                                "Authorization": `Bearer ${sessionStorage.getItem("id_token")})}`
                                            }
                                        });
    } catch (error) {
        console.error(`[API Errors] ${error}`);
    }

    return targetInfo;
}



/**
 * Issue new token
    * API 呼び出し用のトークン発行
 */
const issueToken = async () => {
    console.log(`issueToken : Begin : ${new Date().toISOString()}`); // Debug log

    // URL クエリストリングから認証コードを取得
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");

    // トークン発行のためのパラメータ設定
    const params = new URLSearchParams();
    params.append("grant_type", "authorization_code");
    params.append("client_id", clientId);
    params.append("redirect_uri", location.href.split("?")[0]);
    params.append("code", code);

    try {
        // トークン発行の実行
        let data = await fetchWrapper(`https://${domain}.auth.${region}.amazoncognito.com/oauth2/token`,
                                        {
                                            method: "POST",
                                            headers: {
                                                "Content-Type": "application/x-www-form-urlencoded"
                                            },
                                            body: params.toString(),
                                            redirect: "follow"
                                        });

        sessionStorage.setItem("id_token", data.id_token);
    } catch (error) {
        console.error(error);
    }
}


/**
 * Check the token expired
 * トークン有効期限チェック
 * @param {string} token トークン (IDトークン)
 * @returns {boolean} true: 有効期限切れ, false: 有効期限内
 */
const checkTokenExpried = (token) => {
    // トークンからペイロードを抽出
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");

    const jsonPayload = decodeURIComponent(atob(base64).split("").map((c) => {
        const dg = c.charCodeAt(0).toString(16).padStart(2, "0");
        return `%${dg.slice(-2)}`;
    }).join(""));

    // ペイロードから有効期限を抽出
    const payload = JSON.parse(jsonPayload);
    const expTime = payload.exp;

    // 有効期限チェック結果を返却
    return (expTime * 1000 <= Date.now());
}



/**
 * Lock Control Elements
 * コントロールエレメントの非活性化
 * @param {Boolean} true: 非活性化 (ロック), false: 活性化 (ロック解除)
 */
export const lockControlElements = (lock) => {
    // インプット
    const allInputElements = Array.from(document.querySelectorAll("input"));
    // ボタン
    const allButtonElements = Array.from(document.querySelectorAll("button"));
    const allElements = allInputElements.concat(allButtonElements);

    allElements.forEach(element => {
        if(element.id === "submit") {
            // サブミットボタンは通常 Disabled で別のイベントにて設定
            element.disabled = true;
        } else {
            element.disabled = lock;
        }

        if(element.type === "checkbox" && !lock) {
            element.checked = lock;
        }
    });


    // スピナー (データ転送処理中の円アニメーション)
    document.querySelector("#spinner").style.visibility = lock? "visible" : "hidden";
}



/**
 * Initialize commons
 * アップロード/ダウンロードページの共通的な初期化処理
 */
export const initializeCommons = async () => {
    // Load modules
    Promise.all([
        // AWS favicon
        new Promise((resolve) => {
            const link = document.createElement("link");
            link.href = "https://a0.awsstatic.com/libra-css/images/site/fav/favicon.ico";
            link.type = "image/x-icon";
            link.rel = "icon";
            link.onload = resolve;
            document.head.append(link);
        }),
        // JSZip script */
        new Promise((resolve) => {
            const script = document.createElement("script");
            script.onload = resolve;
            script.src = "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.7.1/jszip.min.js";
            document.head.append(script);
        })
    ]);


    /**
     * Get token for call the API
     * API呼び出し用トークンの取得実行
     */
    // トークンをセッション情報から取得 (発行済み確認)
    const idToken = sessionStorage.getItem("id_token");

    // セッション情報にトークンが存在しない、または取得したトークンが有効期限切れの場合
    if (!idToken || idToken === "undefined" || checkTokenExpried(idToken)) {
        // トークンを発行
        await issueToken();
    }


    /**
     * Back button click event
     * [Back] ボタンクリックイベント
     */
    document.querySelector("#back").addEventListener("click", () => {
        const url = new URL("./entrance.html", location.href);
        const redirectUri = url.href;

        let nextUrl;

        // [Sign-out] チェックボックスがチェックされていた場合、サインアウトする
        if(document.querySelector("#sign-out").checked){
            nextUrl = `https://${domain}.auth.${region}.amazoncognito.com/logout`
                    + `?logout_uri=${redirectUri}`
                    + `&client_id=${clientId}`;
        } else {
            nextUrl = redirectUri;
        }

        location.href = nextUrl;
    });
};
