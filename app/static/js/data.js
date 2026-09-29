(() => {
  let offset=0, total=0;
  const fields=['row_id','MedInc','HouseAge','AveRooms','AveBedrms','Population','AveOccup','Latitude','Longitude','MedHouseVal'];
  const previous=document.querySelector('#previous'), next=document.querySelector('#next');
  async function load(){
    previous.disabled=next.disabled=true;
    const error=document.querySelector('#data-error'); error.hidden=true;
    try{
      const response=await fetch(`/api/data?offset=${offset}&limit=20`);
      const data=await response.json();
      if(!response.ok) throw new Error(data.detail);
      total=data.total;
      const body=document.querySelector('#data-table tbody'); body.replaceChildren();
      for(const row of data.rows){
        const tr=document.createElement('tr');
        for(const field of fields){const td=document.createElement('td'); td.textContent=Number.isInteger(row[field])?row[field]:row[field].toFixed(4); tr.append(td);}
        body.append(tr);
      }
      document.querySelector('#page-status').textContent=`Train: ${offset+1}–${Math.min(offset+20,total)} / ${total} dòng`;
      previous.disabled=offset===0; next.disabled=offset+20>=total;
    }catch(e){error.textContent=e.message;error.hidden=false; document.querySelector('#page-status').textContent='Không đọc được CSDL';}
  }
  previous.addEventListener('click',()=>{offset=Math.max(0,offset-20);load();});
  next.addEventListener('click',()=>{offset+=20;load();});
  load();
})();
