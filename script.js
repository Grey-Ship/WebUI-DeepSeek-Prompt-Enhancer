// Entry point for the extension
export default async function() {
    const style = document.createElement('link');
    style.rel = 'stylesheet';
    style.href = `${extensionsPath}/deepseek-webui-plugin/style.css`;
    document.head.appendChild(style);

    const script = document.createElement('script');
    script.src = `${extensionsPath}/deepseek-webui-plugin/javascript/deepseekPrompts.js`;
    document.head.appendChild(script);
}
