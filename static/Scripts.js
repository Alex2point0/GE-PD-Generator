var TypesArr = [{ text: 'Apple', value: 'Apple', parentKey: 0}, { text: 'Orange', value: 'Orange', parentKey: 1}, { text: 'Mango', value: 'Mango' , parentKey: 2}]


function getValuesByOptionChosen(value) {
return value['parentKey'] == parentKey;}


let parentKey = 1;
var res = TypesArr.filter(getValuesByOptionChosen);
console.log(res);