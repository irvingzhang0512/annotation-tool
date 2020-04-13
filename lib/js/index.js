var urlsArr = [];
var tagsArr = [];
var framesArr = [];
var result = [];
var win;
var isShow = false;
var moveRight = $("#list_left").width();
var type = getUrlParam("type");
var arr = ["unTag", "taged", "checked", "delTag"];
var tab = type && arr.indexOf(type) > -1 ? "#" + type : "#unTag";
$("#myTab a.tab").click(function(e) {
  e.preventDefault();
  $(this).tab("show");
  tab = $(this)[0].hash;
});

function changeFile(e, id) {
  // 首页导入文件时使用
  // 好像就是修改了一下 document.getElementById(id).value 为文件名称
  // 分别是 label.txt -> tagFile, video.txt -> urlFile, frame.txt -> frameFile
  result = [];
  var name = "";
  if (e.files[0]) {
    name = e.files[0].name;
  } 
  document.getElementById(id).value = name;
}

function handleExport(a) {
  // 首页的 `Download` 按钮，将标注好的图片转换为 txt 文件下载

  // 获取标注好的信息
  var result = JSON.parse(localStorage.getItem("result"));
  if (result.length == 0) {
    showTip("The data is empty, unable to export", "warning", "500");
    return;
  }

  // 将信息转换为一行一行的数据，放到列表中
  var newResult = [];
  for (var i in result) {
    for (var j in result[i].tagInfo) {
      newResult.push({
        URLID: result[i].urlId.trim(),
        URL: result[i].url.trim(),
        TagID: result[i].tagInfo[j].tagId,
        Tag: result[i].tagInfo[j].tag,
        Start: result[i].tagInfo[j].start,
        End: result[i].tagInfo[j].end,
        Time: result[i].times,
        State: result[i].state
      });
    }
  }

  
  // 将列表转换为字符串
  // 最后输出字符串为一个文件
  var thObj = newResult[0];
  var thArr = [];
  for (var key in thObj) {
    thArr.push(key);
  }
  var thStr = thArr.join(",");
  var outputArr = [];
  outputArr.push(thStr);
  for (var i in newResult) {
    if (newResult[i].URLID && newResult[i].TagID) {
      var tdObj = newResult[i];
      var tdArr = [];
      for (var key in tdObj) {
        tdArr.push(tdObj[key]);
      }
      outputArr.push(tdArr);
    }
  }
  var str = outputArr.join("\n");
  str = encodeURIComponent(str);
  var now = new Date().format("yyyy-MM-dd_hh.mm.ss");
  a.download = "instruction_" + now + ".txt";
  a.href = "data:text/csv;charset=utf-8,\ufeff" + str;
}

function handleImport() {
  // 首页的 Load 按钮
  // 作用就是导入三个文件

  result = [];
  showTip("loading", "info");

  // 导入 video.txt 文件
  // csv2arr 函数在 config.js 中有定义
  $("input[name=urls]").csv2arr(function (arr) {
    if (arr[0][0].trim() != "URLID" || arr[0][1].trim() != "URL") {
      showTip("Video file format error", "warning", "500");
      $("#tip").fadeOut(100);
      return;
    }
    
    // 去掉文件第一行
    arr.splice(0, 1);

    // 注意，urlsArr 是全局变量
    urlsArr = unique(arr);
    if (urlsArr.length > 0) {
      // 导入 frames.txt 文件
      $("input[name=frames]").csv2arr(function(arr) {
        if (arr[0][0].trim() != "URLID" || arr[0][1].trim() != "Frame") {
          showTip("Frame file format error", "warning", "500");
          $("#tip").fadeOut(100);
          return;
        }

        // 去掉第一行
        arr.splice(0, 1);

        // 注意 frameArr 是全局变量
        framesArr = arr.concat();
        if (framesArr.length > 0) {
          // 导入 label.txt 文件
          $("input[name=tags]").csv2arr(function(arr) {
            if (arr[0][0].trim() != "TagID" || arr[0][1].trim() != "Tag") {
              showTip("Label file format error", "warning", "500");
              $("#tip").fadeOut(100);
              return;
            } else {
              // 去掉第一行
              arr.splice(0, 1);

              // 构建 
              tagsArr = arr.concat();

              // 最主要的函数
              initTable();
            }
          });
        } else {
          showTip("frame data is null", "warning", "500");
          $("#export").hide();
        }
      });
    } else {
      showTip("video data is null", "warning", "500");
      $("#export").hide();
    }
  });
}


function initTable() {
  // 在 Load 函数中调用
  // 功能是将输入的三个文件数据以array的形式保存到 localStorage 中
  $("#unTag").html("");
  $("#taged").html("");
  $("#delTag").html("");
  result = createTable(urlsArr);
  localStorage.setItem("result", JSON.stringify(result));
  localStorage.setItem("tag", JSON.stringify(tagsArr));
  localStorage.setItem("frame", JSON.stringify(framesArr));
}

function handleDelete(e) {
  // 首页中 Unlabeled 中每一条数据都有 Label 和 Delete 两个按钮
  // 本函数就是处理 Delete 按钮的
  var tr = $(e)
    .parent()
    .parent()
    .parent().prevObject[0];
  var urlId = $(tr).find("td")[0].innerText;
  for (var i in result) {
    if (result[i].urlId == parseInt(urlId)) {
      if (tab == "#unTag") {
        localStorage.setItem(
          "unTagTotal",
          parseInt(localStorage.getItem("unTagTotal")) - 1
        );
      } else {
        localStorage.setItem(
          "tagedTotal",
          parseInt(localStorage.getItem("tagedTotal")) - 1
        );
      }
      localStorage.setItem(
        "delTagTotal",
        parseInt(localStorage.getItem("delTagTotal")) + 1
      );
      $("#unTagTotal").html(localStorage.getItem("unTagTotal"));
      $("#tagedTotal").html(localStorage.getItem("tagedTotal"));
      $("#delTagTotal").html(localStorage.getItem("delTagTotal"));
      result[i].state = 2;
      localStorage.setItem("result", JSON.stringify(result));
      $(tr).remove();
      var tr = "<tr><td>" + result[i].urlId;
      tr += "<td>" + result[i].url + "</td>";
      tr += "<td>" + result[i].times + "</td>";
      tr +=
        "<td><button onclick='handleReturn(this)' class='btn btn-danger' type='button'>Restore</button></td>";
      tr += "</tr>";

      if ($("#delTag:has(tbody)").length == 0) {
        $("#delTag table").append("<tbody>" + tr + "</tbody>");
      } else {
        $("#delTag tbody").prepend(tr);
      }
      return;
    }
  }
}


function handleReturn(e) {
  // 应该是 Checked 中每个条目都有的 Cancel 按钮
  var tr = $(e)
    .parent()
    .parent()
    .parent().prevObject[0];
  var urlId = $(tr).find("td")[0].innerText;
  for (var i in result) {
    if (result[i].urlId == parseInt(urlId)) {
      $(tr).remove();
      var tr = "<tr><td>" + result[i].urlId + "</td>";
      tr += "<td>" + result[i].url + "</td>";
      tr += "<td>" + result[i].times + "</td>";

      if (parseInt(result[i].times) > 0) {
        tr +=
          "<td><button onclick='goTag(this)' class='btn btn-info'>Checkout</button><button onclick='handleDelete(this)' class='btn btn-danger' type='button'>Delete</button></td>";
        tr += "</tr>";
        localStorage.setItem(
          "tagedTotal",
          parseInt(localStorage.getItem("tagedTotal")) + 1
        );
        result[i].state = 1;
        if ($("#taged:has(tbody)").length == 0) {
          $("#taged table").append("<tbody>" + tr + "</tbody>");
        } else {
          $("#taged tbody").prepend(tr);
        }
      } else {
        tr +=
          "<td><button onclick='goTag(this)' class='btn btn-info'>Label</button><button onclick='handleDelete(this)' class='btn btn-danger' type='button'>Delete</button></td>";
        tr += "</tr>";
        localStorage.setItem(
          "unTagTotal",
          parseInt(localStorage.getItem("unTagTotal")) + 1
        );
        result[i].state = 0;
        if ($("#unTag:has(tbody)").length == 0) {
          $("#unTag table").append("<tbody>" + tr + "</tbody>");
        } else {
          $("#unTag tbody").prepend(tr);
        }
      }

      localStorage.setItem(
        "delTagTotal",
        parseInt(localStorage.getItem("delTagTotal")) - 1
      );
      $("#unTagTotal").html(localStorage.getItem("unTagTotal"));
      $("#tagedTotal").html(localStorage.getItem("tagedTotal"));
      $("#delTagTotal").html(localStorage.getItem("delTagTotal"));
      localStorage.setItem("result", JSON.stringify(result));
      return;
    }
  }
}

$(function() {
  var param = getUrlParam("type");
  if (param) {
    $('#myTab a[href="#' + param + '"]').tab("show");
  }
  var resultLocal = JSON.parse(localStorage.getItem("result"));
  var tagsArrLocal = JSON.parse(localStorage.getItem("tag"));
  var framesArrLocal = JSON.parse(localStorage.getItem("frame"));
  if (
    resultLocal &&
    tagsArrLocal &&
    framesArrLocal &&
    resultLocal.length > 0 &&
    tagsArrLocal.length > 0 &&
    framesArrLocal.length > 0
  ) {
    urlsArr = resultLocal;
    tagsArr = tagsArrLocal;
    framesArr = framesArrLocal;
    initTable();
  }
  var unTagTotal = localStorage.getItem("unTagTotal")
    ? localStorage.getItem("unTagTotal")
    : 0;
  var tagedTotal = localStorage.getItem("tagedTotal")
    ? localStorage.getItem("tagedTotal")
    : 0;
  var checkedTotal = localStorage.getItem("checkedTotal")
    ? localStorage.getItem("checkedTotal")
    : 0;
  var delTagTotal = localStorage.getItem("delTagTotal")
    ? localStorage.getItem("delTagTotal")
    : 0;
  $("#unTagTotal").html(unTagTotal);
  $("#checkedTotal").html(checkedTotal);
  $("#tagedTotal").html(tagedTotal);
  $("#delTagTotal").html(delTagTotal);
});
