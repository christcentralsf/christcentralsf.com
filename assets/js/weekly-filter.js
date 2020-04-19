function filterSelection(filter) {
  var posts = document.getElementsByClassName("weekly");
  if (filter == "all") posts = "";
  for (var i = 0; i < posts.length; i++) {
    addClass(posts[i], "hide");
    if (posts[i].className.indexOf(filter) > -1) removeClass(posts[i], "hide");
  }
}

function removeFilter() {
  var posts = document.getElementsByClassName("weekly");
  for (var i = 0; i < posts.length; i++) {
    removeClass(posts[i], "hide");
  }
}

function addClass(element, name) {
  var arr1, arr2;
  arr1 = element.className.split(" ");
  arr2 = name.split(" ");
  for (var i = 0; i < arr2.length; i++) {
    if (arr1.indexOf(arr2[i]) == -1) {
      element.className += " " + arr2[i];
    }
  }
}

function removeClass(element, name) {
  var arr1, arr2;
  arr1 = element.className.split(" ");
  arr2 = name.split(" ");
  for (var i = 0; i < arr2.length; i++) {
    while (arr1.indexOf(arr2[i]) > -1) {
      arr1.splice(arr1.indexOf(arr2[i]), 1);
    }
  }
  element.className = arr1.join(" ");
}