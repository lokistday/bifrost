/* A quiet, irregular triangulated surface, rather than a rectangular grid. */
module.exports=function backdrop(){
  const columns=10,rows=6,points=[],edges=new Set(),facets=[];
  for(let y=0;y<=rows;y++)for(let x=0;x<=columns;x++){
    const px=x*90-24+Math.sin(x*2.37+y*1.71)*21;
    const py=y*61-22+Math.sin(x*.83+y*.47)*30+Math.cos(x*.61-y*.91)*17;
    points.push([Number(px.toFixed(1)),Number(py.toFixed(1))]);
  }
  function triangle(a,b,c){
    const ids=[a,b,c];facets.push(`<polygon class="terrain-facet terrain-tone-${facets.length%4}" points="${ids.map(i=>points[i].join(',')).join(' ')}"/>`);
    for(const [u,v] of [[a,b],[b,c],[c,a]])edges.add([Math.min(u,v),Math.max(u,v)].join(':'));
  }
  for(let y=0;y<rows;y++)for(let x=0;x<columns;x++){
    const a=y*(columns+1)+x,b=a+1,c=a+columns+1,d=c+1;
    if((x+y)%2){triangle(a,b,c);triangle(b,d,c);}else{triangle(a,b,d);triangle(a,d,c);}
  }
  const wire=[...edges].map(edge=>{const [a,b]=edge.split(':').map(Number);return'M'+points[a].join(',')+'L'+points[b].join(',');}).join('');
  return `<svg class="hero-terrain" viewBox="0 0 900 370" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">${facets.join('')}<path class="terrain-edges" d="${wire}"/></svg>`;
};
