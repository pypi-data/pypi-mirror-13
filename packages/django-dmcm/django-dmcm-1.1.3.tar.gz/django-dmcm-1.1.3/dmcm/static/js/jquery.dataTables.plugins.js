/**
 * Detect file size type columns automatically. Commonly used for computer
 * file sizes, this can allow sorting to take the order of magnitude indicated
 * by the label (GB etc) into account.
 *
 *  @name File size
 *  @summary Detect abbreviated file size data (8MB, 4KB, 3B, etc)
 *  @author Allan Jardine - datatables.net
 */

jQuery.fn.dataTable.ext.type.detect.unshift( function ( data ) {
    if ( typeof data !== 'string' ) {
        return null;
    }

    var units = data.replace( /[\d\.]/g, '' ).toLowerCase();
    if ( units !== '' && units !== 'b' && units !== 'kb' && units !== 'mb' && units !== 'gb' ) {
        return null;
    }

    return isNaN( parseFloat( data ) ) ?
        null :
        'file-size';
} );

/**
 * When dealing with computer file sizes, it is common to append a post fix
 * such as B, KB, MB or GB to a string in order to easily denote the order of
 * magnitude of the file size. This plug-in allows sorting to take these
 * indicates of size into account.
 * 
 * A counterpart type detection plug-in is also available.
 *
 *  @name File size
 *  @summary Sort abbreviated file sizes correctly (8MB, 4KB, etc)
 *  @author Allan Jardine - datatables.net
 *
 *  @example
 *    $('#example').DataTable( {
 *       columnDefs: [
 *         { type: 'file-size', targets: 0 }
 *       ]
 *    } );
 */

jQuery.fn.dataTable.ext.type.order['file-size-pre'] = function ( data ) {
    var units = data.replace( /[\d\.]/g, '' ).toLowerCase();
    var multiplier = 1;

    if ( units === 'kb' ) {
        multiplier = 1000;
    }
    else if ( units === 'mb' ) {
        multiplier = 1000000;
    }
    else if ( units === 'gb' ) {
        multiplier = 1000000000;
    }

    return parseFloat( data ) * multiplier;
};
