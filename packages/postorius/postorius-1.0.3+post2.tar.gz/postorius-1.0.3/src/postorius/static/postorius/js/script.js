/*
 * Postorius
 *
 * Copyright (C) 1998-2015 by the Free Software Foundation, Inc.
 *
 * This file is part of Postorius.
 *
 * Postorius is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option)
 * any later version.
 *
 * Postorius is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * Postorius.  If not, see <http://www.gnu.org/licenses/>.
 *
 */


$(function() {

    /* Pagination */
    $(".pager .pager-select a").click(function(e) {
        e.preventDefault();
        $(this).hide();
        $(this).next("form").css("display", "inline-block");
    });
    $(".pager .pager-select form select").change(function() {
        $(this).closest("form").submit();
    });

});
