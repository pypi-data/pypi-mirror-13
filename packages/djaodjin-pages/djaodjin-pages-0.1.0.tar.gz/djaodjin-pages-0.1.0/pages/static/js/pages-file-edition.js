/* global $ ace document themePackageSlug fileEditionUrl loadedTemplate window:true */

$(document).ready(function() {
    "use strict";
    // load ace and extensions
    var editor = ace.edit("editor");
    var oldText = null;
    editor.setTheme("ace/theme/monokai");
    editor.setOption({
        enableEmmet: true,
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: false});
    editor.setValue("");

    var loadFile = function(filePath){
        $.ajax({
            url: fileEditionUrl + "filepath" + filePath,
            method: "GET",
            datatype: "json",
            contentType: "application/json; charset=utf-8",
            success: function(data){
                oldText = data.text;
                editor.setValue(data.text);
                var modelist = ace.require("ace/ext/modelist");
                var mode = modelist.getModeForPath(filePath).mode;
                var modename = mode.split("/");
                modename = modename[modename.length - 1];
                $("#mode").val(modename);
                editor.getSession().setMode(mode);
                editor.focus();
                editor.gotoLine(0);
                $("#save-edition").data("filepath", filePath);
                $("#opened-file").text(filePath);
                $("#status-file").text("");
            }
        });
    };

    $("#save-edition").click(function(){
        var newText = editor.getValue();
        var filePath = $(this).data("filepath");
        $.ajax({
            url: fileEditionUrl + "filepath" + filePath,
            method: "PUT",
            data: JSON.stringify({
                text: newText}),
            datatype: "json",
            contentType: "application/json; charset=utf-8",
            success: function(){
                oldText = newText;
                $("#status-file").text("Saved!");
            }
        });
    });

    editor.getSession().on("change", function() {
        if (oldText !== editor.getValue()){
            $("#status-file").text("Modified. Do not forget to save");
        }else{
            $("#status-file").text("");
        }
    });

    editor.commands.addCommand({
        name: "save",
        bindKey: {win: "Ctrl-s", mac: "Command-s"},
        exec: function() {
            $("#save-edition").trigger("click");
        },
        readOnly: true
    });

    $("#mode").change(function(){
        editor.getSession().setMode("ace/mode/" + $(this).val());
    });

    $(".pages-edit-file").click(function(event){
        event.preventDefault();
        var filepath = $(this).data("filepath");
        loadFile(filepath);
    });

    $(".pages-show-file").click(function(event){
        event.preventDefault();
        var $i = $(this).prev();
        if ($i.hasClass("fa-folder")){
            $(this).prev().addClass("fa-folder-open").removeClass("fa-folder");
        }else{
            $(this).prev().addClass("fa-folder").removeClass("fa-folder-open");
        }
        var $ul = $(this).parent().next();
        $ul.toggle();
    });

    $(".pages-edit-file[data-filepath=\"" + loadedTemplate + "\"]").trigger("click");

    $("#edit-file-by-name").click(function(event){
        event.preventDefault();
        var href = $(this).data("href");
        var fileToEdit = $("#file-name-input").val();
        if (fileToEdit !== ""){
            href += "&template_loaded=" + fileToEdit;
        }
        window.location = href;
    });
});
