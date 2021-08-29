var slider = document.getElementById("xp-slider");
var output = document.getElementById("xp-value");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
}


async function createLevelAction() {
//GEt The values of both the fields 
//check if the value if correct or no
//check if the no of roles are less than 15 
//check if there is already a level for that specific level
//chekc if there is alr a role for that level
//throw notification if invalid 
//if good/
//clear both the fields 
//append the values in format to the js visula fields
//assgin the values same name or id throught which we can easilyu identify when processing server side request
//send a notifcation in grreent rext that it is done

  var levelNo = document.getElementById("level-input").value
  var levelRoleID = document.getElementById("level-role").value
  var levelRole = document.getElementById("select2-level-role-container").innerText
  var levelNotice = document.getElementById("level-notice")

  var parentDiv = document.getElementById("js-visual")



  if (levelNo < 1 || levelNo > 100) {
    console.log("Number invaid")
    levelNotice.innerHTML = "Level Range should be between 1-100"
    return
  }

  parentDivChildren = parentDiv.children
  levels_present = []
  
  for (var i = 0; i < parentDivChildren.length; i++) {
    levels_present.push(parentDivChildren[i].id);
  }
  
  if (levels_present.includes("level-" + levelNo)) {
    console.log("Cant add more than one role to one level")
    levelNotice.innerHTML =  "Each level can only have one role maximum"
    return
  }

  entryNo = parentDiv.children.length
  if (entryNo > 14) {
    console.log("Maximun limit for levels is 15")
    levelNotice.innerHTML = "Maximun limit for levels is 15"
    return
  } 


//check if the input data is valid int or not is there a role with that name or snot 

  function setAttrs(elm, attrs) {
    for(var key in attrs) {
      elm.setAttribute(key, attrs[key])
    }
  }




  
 

  mainDiv = document.createElement("div")
  mainDiv.setAttribute("class", "js-display")
  mainDiv.setAttribute("id", "level-" + levelNo)
  parentDiv.appendChild(mainDiv)


  levelInput = document.createElement("input")
  roleInput = document.createElement("input")

  setAttrs(levelInput, {
    "class": "display-input",
    "type": "text",
    "readonly": "readonly",
    "value": "Level " + levelNo,
    "name": "entry"+ levelNo + "," + levelNo})

  setAttrs(roleInput, {
    "class": "display-input",
    "type": "text",
    "readonly": "readonly",
    "value": levelRole,
    "name": "entry"+ levelNo + "," + levelRoleID })

  mainDiv.appendChild(levelInput)
  mainDiv.appendChild(roleInput)
  

  //createing Delete Button
  deleteBtn = document.createElement("button")
  deleteBtn.innerText = "-Remove"
  setAttrs(deleteBtn, {"onclick": "deleteThisLevelAction(level-" + levelNo + ")",  "class": "level-remove", "type": "button", "name": "entry"+ levelNo  } )

  mainDiv.appendChild(deleteBtn)




  //<id="display-3">
  //<input value="Level 69" name="LAASDFA" >
  //<input value="YO HO HO ROLE" name ="LAA"
  //<button onclick="deleteThisLevelAction()" class="level-remove">-Remove</button>
//</div>


  //await new Promise(r => setTimeout(r, 2000));




};

function deleteThisLevelAction(id) {
  deleteElement = document.getElementById(id)
  deleteElement.remove()
}