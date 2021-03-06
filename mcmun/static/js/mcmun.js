var localStorageSupported = function() {
  try {
      return 'localStorage' in window && window['localStorage'] !== null;
    } catch (e) {
        return false;
    }
};

var registerEasterEgg = function(hashName, imageName, message) {
    if (window.location.hash === '#' + hashName) {
        $('.photo img').attr('src', '/static/img/sec/' + imageName + '.jpg');
        $('.bio p').remove();
        $('.bio').append('<p>' + message + '</p>');

        $('#sec-bios').scrollTop();
    }
};

$(document).ready(function() {
    // Promo video stuff. Hidden on small screens (through CSS).
    var isLocalStorageSupported = localStorageSupported();
    if (!isLocalStorageSupported || !localStorage.getItem('seen_promo')) {
        var overlay = document.createElement('div');
        overlay.id = 'overlay';
        overlay.innerHTML = '<div class="content">' +
            '<h1>If you haven\'t seen our promo video ...</h1>' +
            '<object width="960" height="540">' +
            '<param name="movie"' +
                   'value="http://www.youtube.com/v/vAm-3UWzz64">' +
            '<param name="allowScriptAccess" value="always"></param>' +
            '<embed src="http://www.youtube.com/v/vAm-3UWzz64"' +
                   'type="application/x-shockwave-flash"' +
                   'allowscriptaccess="always"' +
                   'width="960" height="540"></embed>' +
            '</object>' +
            '</div>' +
            '<div class="close">×</div>';
      //  $('body').append(overlay);

        if (isLocalStorageSupported) {
            // Don't force the user to watch the video again
            localStorage.setItem('seen_promo', true);
        }

        $('#overlay .close').click(function () {
            $('#overlay').hide();
        });
    }

    // Staff coordinator application form
    if ($('#staff-coordinator-form').length) {
        // Hide the ones that don't always need to be filled
        $('#id_occc_experience').parent().parent().hide();
        $('#id_event_experience').parent().parent().hide();

        // Show them if the right thing is selected as a preferred position
        $('#staff-coordinator-form select[id^="id_preferred_position"]').change(function () {
            var selected = $(this).find('option:selected').val();

            // Truly awful
            if (selected === 'events-coord' || selected === 'events-tl') {
                $('#id_event_experience').parent().parent().show();
            } else {
                // lol
                if (!$('#staff-coordinator-form select[id^="id_preferred_position"] option[value^="events"]:selected').length) {
                    $('#id_event_experience').parent().parent().hide();
                }
            }

            if (selected === 'occc') {
                $('#id_occc_experience').parent().parent().show();
            } else {
                if (!$('#staff-coordinator-form select[id^="id_preferred_position"] option[value^="occc"]:selected').length) {
                    $('#id_occc_experience').parent().parent().hide();
                }
            }
        });
    }

    // If any element on the page has an ID of collapsible, make the h2+ headings collapsible
    if ($('#collapsible').length) {
        var headings = 'h2,h3,h4,h5,h6';

        $(headings).each(function (index, heading) {
            // Add the [-] / [+] thing
            this.innerHTML += ' <a href="#" class="toggle-collapse">[-]</a>';
        });

        $('#content').on('click', '.toggle-collapse', function (event) {
            var heading = this.parentNode;
            var headingTag = heading.localName;

            // Get all the headings at this level or bigger
            var relevantHeadings = headings.substr(0, headings.indexOf(headingTag) + 2);
            var section = $(heading).nextUntil(relevantHeadings);

            // kind of buggy - if a child is hidden and a parent is hidden then shown, it won't match up
            if ($(this).hasClass('collapsed')) {
                $(section).show();
                this.innerText = '[-]';
            } else {
                $(section).hide();
                this.innerText = '[+]';
            }

            $(this).toggleClass('collapsed');

            return false;
        });
    }

    if ($('#carousel').length) {
        var rotateTimeout = 3500;
        var firstDiv = $('#carousel .slide')[0];
        var rotateCarousel = function () {
            var nextDiv = $('#carousel .active').next()[0] || firstDiv;
            setTimeout(rotateCarousel, rotateTimeout);
            $('.active').removeClass('active');
            $(nextDiv).addClass('active');
        };
    }

    timeout = setTimeout(rotateCarousel, rotateTimeout);

    if ($('#sec-bios').length) {
        // Show the person's title upon hovering over the photo
        $('#sec-bios').delegate('.photo', 'mouseenter', function (event) {
            var title = $(this).next().find('h3').text();
            $(this).append('<div class="title-hover">' + title + '</div>');
            $('.title-hover').fadeIn(300);
        })
        .delegate('.photo', 'mouseleave', function (event) {
            $('.title-hover').remove();
        })
        .delegate('.photo', 'click', function (event) {
            $('.active').removeClass('active');
            $('.bio').hide();
            $(this).addClass('active').next().show();
        });

        // Hacky deep-linking
        var hash = window.location.hash;
        if (hash) {
            var desiredBio = $('#sec-bios').find(hash);
            if (desiredBio) {
                $('.bio').hide();
                $(desiredBio).addClass('active').next().show();
            }
        }

        // Register the easter eggs (on the secretariat page)
        registerEasterEgg('abdaal', 'lolabdaal', 'ALL HAIL GLORIOUS LEADER');
        registerEasterEgg('pikachu', 'pikachu', 'I LOVE PIKACHU');
        registerEasterEgg('ryan', 'lolryan', 'you should see me twerking');
    }

    var delegationFee = 75;

    $('#fee-calculator').delegate('select', 'change', function (event) {
        var numDelegates = parseInt($('#num-delegates option:checked').val(), 10);
        var registrationType = $('#registration-type option:checked').val();

        // Only show the fee information stuff when everything has been selected
        if (numDelegates > 0 && registrationType !== '') {
            var delegateFee, totalFee, deposit, remainder;

            switch (registrationType) {
                case 'priority':
                    delegateFee = 85;
                break;
                case 'regular':
                    delegateFee = 95;
                break;
                case 'international':
                    delegateFee = 60;
                break;
            }

            if (delegateFee) {
                totalFee = numDelegates * delegateFee + delegationFee;
                deposit = delegationFee + (numDelegates * delegateFee) * 0.5;
                remainder = totalFee - deposit;

                $('#fee-information').text('Your total fee, for ' + numDelegates + ' delegates and ' + registrationType + ' registration, is $' + totalFee.toFixed(2) + '. If you wish to pay using the tiered system, your deposit would be $' + deposit.toFixed(2) + ', and the remainder would be $' + remainder.toFixed(2) + '.');
            } else {
                // Someone is mucking about with the form
                $('#fee-information').text("Please stop messing with the form. There's nothing interesting here.");
            }
            $('#fee-information').show();
        }
    });

    // Handle stuff for the registration form
    var priorityOption = $('#priority-dt');
    if (priorityOption.length) {
        // Has to be done this way for now because dl only allows dt, dd (fix later)
        priorityOption.hide().next().hide();
        $('#id_country').change(function () {
            var country = $(this).val();

            // The priority registration option is only valid for North America
            if (country === 'CA' || country === 'US') {
                priorityOption.show().next().show();
            } else {
                priorityOption.hide().next().hide();
            }
        });
    }

    // Make sure that a size is selected when ordering a shirt, or a bundle
    // containing a shirt.
    var merchandiseForms = $('.merchandise-form');
    if (merchandiseForms.length) {
        merchandiseForms.filter(function () {
            return $(this).find('#id_size').length;
        }).submit(function () {
            var size = $(this).find('#id_size').val();

            if (!size) {
                alert('You must select a size!');
                return false;
            }
        });
    }
});
