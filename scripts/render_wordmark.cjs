/* Solid letter faces with one open wireframe depth cell behind them. */
module.exports = function wordmark() {
  const letters = [
    {w:70,c:[[[0,0],[47,0],[64,12],[64,39],[54,48],[68,58],[68,86],[54,100],[0,100]],[[20,18],[42,18],[46,22],[46,35],[40,40],[20,40]],[[20,58],[44,58],[49,63],[49,77],[43,82],[20,82]]]},
    {w:22,c:[[[0,0],[22,0],[22,100],[0,100]]]},
    {w:66,c:[[[0,0],[66,0],[66,20],[22,20],[22,40],[56,40],[56,60],[22,60],[22,100],[0,100]]]},
    {w:72,c:[[[0,0],[48,0],[66,16],[66,43],[52,56],[72,100],[48,100],[27,60],[20,60],[20,100],[0,100]],[[20,19],[40,19],[46,25],[46,37],[40,43],[20,43]]]},
    {w:72,c:[[[16,0],[56,0],[72,16],[72,84],[56,100],[16,100],[0,84],[0,16]],[[24,20],[48,20],[52,24],[52,76],[48,80],[24,80],[20,76],[20,24]]]},
    {w:68,c:[[[68,0],[68,20],[24,20],[20,24],[20,36],[24,40],[50,40],[68,56],[68,84],[52,100],[0,100],[0,80],[44,80],[48,76],[48,64],[44,60],[18,60],[0,44],[0,16],[16,0]]]},
    {w:72,c:[[[0,0],[72,0],[72,20],[47,20],[47,100],[25,100],[25,20],[0,20]]]},
    {w:18,c:[[[0,82],[18,82],[18,100],[0,100]]]}
  ];
  let x=8, body='';
  const dx=10,dy=-11;
  for (const [i,glyph] of letters.entries()) {
    const d=glyph.c.map(c=>'M'+c.map(([a,b])=>`${a},${b}`).join('L')+'Z').join('');
    let ties='';
    for(const contour of glyph.c)for(let j=0;j<contour.length;j++){
      const a=contour[j],b=contour[(j+1)%contour.length];
      const steps=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/12));
      for(let k=0;k<steps;k++){
        const u=a[0]+(b[0]-a[0])*k/steps,v=a[1]+(b[1]-a[1])*k/steps;
        ties+=`M${u.toFixed(2)},${v.toFixed(2)}l${dx},${dy}`;
      }
    }
    body+=`<g data-wire-glyph data-contours='${JSON.stringify(glyph.c)}' data-offset="${x}" transform="translate(${x},40)">
      <g class="brand-wire-depth"><path data-wire-back d="${d}" transform="translate(${dx},${dy})"/><path data-wire-ties d="${ties}"/></g>
      <path class="brand-wire-front" d="${d}" fill-rule="evenodd"/></g>`;
    x+=glyph.w+(i===6?12:18);
  }
  return `<svg class="brand-wireframe" data-brand-width="${x+dx}" viewBox="0 0 ${x+dx} 152" fill="none" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">${body}</svg>`;
};
