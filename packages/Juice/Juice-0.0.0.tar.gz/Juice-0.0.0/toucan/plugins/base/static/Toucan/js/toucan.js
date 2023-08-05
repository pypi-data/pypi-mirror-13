
var Toucan = {

    /**
    Google Analytics tracking
    **/
    track_event: function(category, action, label, value) {
        if (typeof ga !== 'undefined') {
            ga("send", "event", category, action, label, value)
        }
    },

    //------

    /**
    BASIC Login
    **/
    basic_login: function() {
        var that = this
        $("#toucan-login-login-form").submit(function(e){
            e.preventDefault();
            that.track_event("User", "LOGIN", "Email")
            this.submit()
        })
        $("#toucan-login-signup-form").submit(function(e){
            e.preventDefault();
            that.track_event("User", "SIGNUP", "Email")
            this.submit()
        })
        $("#toucan-login-lostpassword-form").submit(function(e){
            e.preventDefault();
            that.track_event("User", "LOSTPASSWORD", "Email")
            this.submit()
        })
    },

    /**
     * Setup Authomatic
     */
    setup_authomatic: function(redirect) {
        authomatic.setup({
            onLoginComplete: function(result) {
                switch(result.custom.action) {
                    case "redirect":
                        location.href = result.custom.url
                        break
                    default:
                        if (redirect == "") {
                            redirect = "/"
                        }
                        location.href = redirect
                        break
                }
            }
        })

        authomatic.popupInit()
    },

    /**
     * A function that launch a modal and return a callback to access the clicked element
     * @param el
     * @param callback
     */
    onModalShow: function(el, callback) {
        $(el).on("show.bs.modal").on('show.bs.modal', function (event) {
            var button = $(event.relatedTarget) // Button that triggered the modal
            var modal = $(this)
            callback(button, modal)
        })

    },

    init: function() {

        // Lazy load images
        $("img.lazy").lazy({
            effect: "fadeIn",
            effectTime: 1000
        })

        // Oembed
        $("a.WM-oembed").oembed(null, {
            includeHandle: false,
            maxWidth: "100%",
            maxHeight: "480",
        });

        // Share buttons
        $(".WM-share-buttons").each(function(){
            var el = $(this)
            el.jsSocials({
                url: el.data("url"),
                text: el.data("text"),
                showCount: el.data("show-count"),
                showLabel: el.data("show-label"),
                shares:el.data("buttons"),
                _getShareUrl: function() {
                    var url = jsSocials.Socials.prototype._getShareUrl.apply(this, arguments);
                    var width = 550;
                    var height = 420;
                    var winHeight = screen.height, winWidth = screen.width;
                    var left = Math.round((winWidth / 2) - (width / 2));
                    var top = (winHeight > height) ? Math.round((winHeight / 2) - (height / 2)) : 0;
                    var options = "scrollbars=yes,resizable=yes,toolbar=no,location=yes" + ",width=" + width + ",height=" + height + ",left=" + left + ",top=" + top;
                    return "javascript:window.open('" + url + "', 'Sharing', '"+ options +"')";
                }
            });

        })

    }
}


$(function(){
    Toucan.init()
})