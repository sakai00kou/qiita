/**
 * Import module
 * モジュールの読み込み
 */
// 環境変数
import { USERPOOL_DOMAIN, USERPOOL_REGION, USERPOOL_CLIENT_ID, USERPOOL_RESPONSE_TYPE, USERPOOL_SCOPE} 
    from "./env-vals.js";



/**
 * Environment valiables
 * 環境変数
 */
const domain = USERPOOL_DOMAIN;
const region = USERPOOL_REGION;
const clientId = USERPOOL_CLIENT_ID;
const responseType = USERPOOL_RESPONSE_TYPE;
const scope = USERPOOL_SCOPE;



/**
 * DOM Content Loaded event
 * DOMコンテントロード後イベント
 */
window.addEventListener("DOMContentLoaded", () => {
    // Load AWS favicon
    new Promise((resolve) => {
        const link = document.createElement("link");
        link.href = "https://a0.awsstatic.com/libra-css/images/site/fav/favicon.ico";
        link.type = "image/x-icon";
        link.rel = "icon";
        link.onload = resolve;
        document.head.append(link);
    });


    /**
     * Button click event
     * アップロードとダウンロードのボタンクリックイベント
     */
    const allButtons = document.querySelectorAll("button");
    allButtons.forEach(button => {
        button.addEventListener("click", () => {
            allButtons.disabled = true;

            const url = new URL(button.value, location.href);
            const redirectUri = url.href;

            // サインイン(認証)ページ URL
            const cognitoUrl = `https://${domain}.auth.${region}.amazoncognito.com/login`
                                + `?response_type=${responseType}`
                                + `&client_id=${clientId}`
                                + `&redirect_uri=${redirectUri}`
                                + `&scope=${scope}`;

            // サインイン(認証)ページへ移動
            location.href = cognitoUrl;
        });
    });
});
