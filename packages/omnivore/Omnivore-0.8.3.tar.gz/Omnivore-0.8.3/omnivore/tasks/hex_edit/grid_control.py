# peppy Copyright (c) 2006-2010 Rob McMullen
# Licenced under the GPLv2; see http://peppy.flipturn.org for more info
import os
import struct

import wx
import wx.grid as Grid
import wx.lib.newevent

from omnivore.utils.wx.bytegrid import ByteGridTable, ByteGrid

from omnivore.framework.actions import *
from actions import *
from commands import ChangeByteCommand

import logging
log = logging.getLogger(__name__)

# Grid tips:
# http://www.blog.pythonlibrary.org/2010/04/04/wxpython-grid-tips-and-tricks/


class ImageCache(object):
    def __init__(self, width=-1, height=-1):
        self.width = width
        self.height = height
        self.cache = {}
    
    def invalidate(self):
        self.cache = {}
    
    def set_colors(self, editor):
        self.color = editor.text_color
        self.font = editor.text_font
        self.selected_background = editor.highlight_color
        self.selected_brush = wx.Brush(editor.highlight_color, wx.SOLID)
        self.selected_pen = wx.Pen(editor.highlight_color, 1, wx.SOLID)
        self.normal_background = editor.background_color
        self.normal_brush = wx.Brush(editor.background_color, wx.SOLID)
        self.normal_pen = wx.Pen(editor.background_color, 1, wx.SOLID)
        self.cursor_background = editor.background_color
        self.cursor_brush = wx.Brush(editor.background_color, wx.TRANSPARENT)
        self.cursor_pen = wx.Pen(editor.unfocused_cursor_color, 2, wx.SOLID)
        self.match_background = editor.match_background_color
        self.match_brush = wx.Brush(editor.match_background_color, wx.SOLID)
        self.match_pen = wx.Pen(editor.match_background_color, 1, wx.SOLID)
        self.comment_background = editor.comment_background_color
        self.comment_brush = wx.Brush(editor.comment_background_color, wx.SOLID)
        self.comment_pen = wx.Pen(editor.comment_background_color, 1, wx.SOLID)
    
    def draw_blank(self, dc, rect):
        dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
        dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
        dc.DrawRectangleRect(rect)
    
    def draw_text(self, dc, rect, text, style):
        k = (text, style, rect.width, rect.height)
        try:
            bmp = self.cache[k]
        except KeyError:
            bmp = wx.EmptyBitmap(rect.width, rect.height)
            mdc = wx.MemoryDC()
            mdc.SelectObject(bmp)
            r = wx.Rect(0, 0, rect.width, rect.height)
            self.draw_text_to_dc(mdc, r, text, style)
            del mdc  # force the bitmap painting by deleting the gc
            self.cache[k] = bmp
        dc.DrawBitmap(bmp, rect.x, rect.y)
    
    def draw_text_to_dc(self, dc, rect, text, style):
        if style == -1:
            dc.SetBrush(self.selected_brush)
            dc.SetPen(self.selected_pen)
            dc.SetTextBackground(self.selected_background)
        elif style & 1:
            dc.SetPen(self.match_pen)
            dc.SetBrush(self.match_brush)
            dc.SetTextBackground(self.match_background)
        elif style & 128:
            dc.SetPen(self.comment_pen)
            dc.SetBrush(self.comment_brush)
            dc.SetTextBackground(self.comment_background)
        else:
            dc.SetPen(self.normal_pen)
            dc.SetBrush(self.normal_brush)
            dc.SetTextBackground(self.normal_background)
        dc.SetBackgroundMode(wx.SOLID)
        dc.DrawRectangleRect(rect)
        dc.SetTextForeground(self.color)
        dc.SetFont(self.font)
        dc.DrawText(text, rect.x+1, rect.y+1)


class CachingHexRenderer(Grid.PyGridCellRenderer):
    def __init__(self, table, editor, cache):
        """Render data in the specified color and font and fontsize"""
        Grid.PyGridCellRenderer.__init__(self)
        self.table = table
        self.cache = cache
        cache.set_colors(editor)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        index, _ = self.table.get_index_range(row, col)
        if not self.table.is_index_valid(index):
            self.cache.draw_blank(dc, rect)
        else:
            text, style = self.table.get_value_style(row, col)
            start, end = grid.editor.anchor_start_index, grid.editor.anchor_end_index
            if start > end:
                start, end = end, start
#            print "r,c,index", row, col, index, "grid selection:", start, end
            is_in_range = start <= index < end
            if is_in_range:
                style = -1
            self.cache.draw_text(dc, rect, text, style)

            r, c = self.table.get_row_col(grid.editor.cursor_index)
            if row == r and col == c:
                dc.SetPen(self.cache.cursor_pen)
                dc.SetBrush(self.cache.cursor_brush)
                x = rect.x+1
                if sys.platform == "darwin":
                    w = rect.width - 2
                    h = rect.height - 2
                else:
                    w = rect.width - 1
                    h = rect.height - 1
                dc.DrawRectangle(rect.x+1, rect.y+1, w, h)


class ByteTable(ByteGridTable):
    def __init__(self, bytes_per_row=16):
        ByteGridTable.__init__(self)
        
        self._debug=False
        self.bytes_per_row = bytes_per_row
        self._cols = self.bytes_per_row
        self._rows = 0

    def set_editor(self, editor):
        self.editor = editor
        self.segment = segment = self.editor.segment
        self.start_offset = segment.start_addr & 0x0f
        self._rows=((self.start_offset + len(segment) - 1) / self.bytes_per_row) + 1
        log.debug("segment %s: rows=%d cols=%d len=%d" % (segment, self._rows, self.bytes_per_row, len(segment)))
    
    def get_index_range(self, row, col):
        """Get the byte offset from start of file given row, col
        position.
        """
        index = row * self.bytes_per_row + col - self.start_offset
        return index, index + 1

    def get_row_col(self, index):
        return divmod(index + self.start_offset, self.bytes_per_row)

    def is_index_valid(self, index):
        return 0 <= index < len(self.segment)
    
    def get_col_size(self, col):
        return 2

    def get_value_style_upper(self, row, col):
        i, _ = self.get_index_range(row, col)
        return "%02X" % self.segment[i], self.segment.style[i]

    def get_value_style_lower(self, row, col):
        i, _ = self.get_index_range(row, col)
        return "%02x" % self.segment[i], self.segment.style[i]

    def GetRowLabelValue(self, row):
        return self.segment.label(row*self.bytes_per_row - self.start_offset, self.get_value_style == self.get_value_style_lower)

    def GetColLabelValue(self, col):
        if self.get_value_style == self.get_value_style_lower:
            return "%x" % col
        return "%X" % col

    def SetValue(self, row, col, value):
        val=int(value,16)
        if val>=0 and val<256:
            i, _ = self.get_index_range(row, col)
            if self.is_index_valid(i):
                self.segment[i:i+1] = val
                return True
            log.debug('SetValue(%d, %d, "%s")=%d index %d out of range.' % (row, col, value, val, i))
            return False
        else:
            log.debug('SetValue(%d, %d, "%s")=%d out of range.' % (row, col, value, val))
            return False

    def ResetViewProcessArgs(self, grid, editor, *args):
        grid.image_cache.invalidate()
        self.set_editor(editor)


class HexEditControl(ByteGrid):
    """
    View for editing in hexidecimal notation.
    """

    def __init__(self, parent, task, **kwargs):
        """Create the HexEdit viewer
        """
        table = ByteTable()
        ByteGrid.__init__(self, parent, task, table, **kwargs)
        self.image_cache = ImageCache()
    
    def get_grid_cell_renderer(self, table, editor):
        return CachingHexRenderer(table, editor, self.image_cache)
    
    def change_value(self, row, col, text):
        """Called after editor has provided a new value for a cell.
        
        Can use this to override the default handler.  Return True if the grid
        should be updated, or False if the value is invalid or the grid will
        be updated some other way.
        """
        try:
            val = int(text,16)
            if val >= 0 and val < 256:
                start, end = self.table.get_index_range(row, col)
                if self.table.is_index_valid(start):
                    cmd = ChangeByteCommand(self.table.segment, start, end, val)
                    self.task.active_editor.process_command(cmd)
        except ValueError:
            pass
        return False
    
    def get_popup_actions(self, r, c):
        return [CutAction, CopyAction, PasteAction, None, SelectAllAction, SelectNoneAction, GetSegmentFromSelectionAction]
