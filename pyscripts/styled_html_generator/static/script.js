function convertToRuby(text) {
    return text.replace(/「([^」]+)」/g, (match, content) => {
        if (!/\|/.test(content)) {
            return match; // 如果花括号内没有竖线，保持原样
        }

        const [characters, pinyins] = content.split('|');
        const chars = characters.trim().split('');
        const pinyinArray = pinyins.trim().split(/\s+/);

        let result = '<div class="poem-line">';
        let pinyinIndex = 0;
        for (let i = 0; i < chars.length; i++) {
            const char = chars[i];
            let pinyin = '';
            if (/[，。、！？]/.test(char)) {
                result += `<span class="char-wrapper"><span class="pinyin"></span><span class="punctuation">${char}</span></span>`;
            } else {
                if (pinyinIndex < pinyinArray.length) {
                    pinyin = pinyinArray[pinyinIndex];
                    pinyinIndex++;
                }
                result += `<span class="char-wrapper"><span class="pinyin">${pinyin}</span><span class="hanzi">${char}</span></span>`;
            }
        }
        result += '</div>';
        return result;
    });
}

const brPlugin = {
  "after:highlightElement": ({ el, result, text }) => {
    //console.log(el);
    //console.log(el.childNodes)
    var space_re = new RegExp("^ +$");
    el.childNodes.forEach((node, idx)=>{
      if (node.nodeName == '#text' && node.nodeValue.match(space_re)){
        if (idx > 0) {
            el.childNodes[idx-1].innerHTML = el.childNodes[idx-1].innerHTML + node.nodeValue;
        }
        else {
            el.childNodes[idx+1].innerHTML = node.nodeValue + el.childNodes[idx+1].innerHTML;
        }

      }
    })
    el.innerHTML = el.innerHTML.replace(/\n/g, '<br>');
  }
};

hljs.addPlugin(brPlugin);
hljs.highlightAll();

var clipboard = new ClipboardJS('.btn');

clipboard.on('success', function(e) {
  console.info('Copy successfully.')
  console.info('Action:', e.action);
  console.info('Trigger:', e.trigger);

  e.clearSelection();
});

clipboard.on('error', function(e) {
  console.error('Action:', e.action);
  console.error('Trigger:', e.trigger);
});
