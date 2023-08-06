import sys

import numpy as np
import wx
import wx.grid as Grid

import logging
log = logging.getLogger(__name__)


class FontGridRenderer(Grid.PyGridCellRenderer):
    def __init__(self, table, editor):
        """Render data in the specified color and font and fontsize"""
        Grid.PyGridCellRenderer.__init__(self)
        self.table = table
        self.color = editor.text_color
        self.font = editor.text_font
        self.selected_background = editor.highlight_color
        self.selected_brush = wx.Brush(editor.highlight_color, wx.SOLID)
        self.selected_pen = wx.Pen(editor.highlight_color, 1, wx.SOLID)
        self.normal_background = editor.background_color
        self.normal_brush = wx.Brush(editor.background_color, wx.SOLID)
        self.normal_pen = wx.Pen(editor.background_color, 1, wx.SOLID)
        self.colSize = None
        self.rowSize = 50

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        # Here we draw text in a grid cell using various fonts
        # and colors.  We have to set the clipping region on
        # the grid's DC, otherwise the text will spill over
        # to the next cell
        dc.SetClippingRect(rect)

        # clear the background
        dc.SetBackgroundMode(wx.SOLID)
        
        index, _ = self.table.get_index_range(row, col)
        if not self.table.is_index_valid(index):
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
            dc.DrawRectangleRect(rect)
        else:
            dc.SetBrush(self.normal_brush)
            dc.SetPen(self.normal_pen)
            dc.SetTextBackground(self.normal_background)
            dc.DrawRectangleRect(rect)

            text = self.table.GetValue(row, col)
            dc.SetBackgroundMode(wx.SOLID)

            dc.SetTextForeground(self.color)
            dc.SetFont(self.font)
            dc.DrawText(text, rect.x+1, rect.y+1)

        dc.DestroyClippingRegion()


class FontGridTable(Grid.PyGridTableBase):
    def __init__(self, column_size=20):
        Grid.PyGridTableBase.__init__(self)
        
        self.col_size = 20
        self.parse_tile_map([("test", np.arange(0,10, dtype=np.uint8))])
    
    def parse_tile_map(self, tile_map):
        self.tile_map = tile_map
        self._rows = len(tile_map)
        self._cols = 0
        for label, chars in tile_map:
            n = np.alen(chars)
            if n > self._cols:
                self._cols = n
    
    def get_index_range(self, row, col):
        """Get the byte offset from start of file given row, col
        position.
        """
        index = row * self.bytes_per_row + col
        return index, index

    def get_row_col(self, index):
        return divmod(index, self.bytes_per_row)

    def is_index_valid(self, index):
        return index < self._rows * self._cols
    
    def get_col_size(self, c):
        return self.column_sizes[c]
    
    def get_col_type(self, c):
        return "hex"
   
    def GetNumberRows(self):
        return self._rows

    def GetRowLabelValue(self, row):
        return self.tile_map[row][0]

    def GetNumberCols(self):
        return self._cols

    def GetColLabelValue(self, col):
        return ""
    
    def GetValue(self, row, col):
        label, chars = self.tile_map[row]
        if col >= np.alen(chars):
            return ""
        return str(chars[col])

    def SetValue(self, row, col, value):
        raise NotImplementedError

    def ResetViewProcessArgs(self, *args):
        pass

    def ResetView(self, grid, *args):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        oldrows=self._rows
        oldcols=self._cols
        self.ResetViewProcessArgs(*args)
        
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (oldrows, self._rows, Grid.GRIDTABLE_NOTIFY_ROWS_DELETED, Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (oldcols, self._cols, Grid.GRIDTABLE_NOTIFY_COLS_DELETED, Grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:

            if new < current:
                msg = Grid.GridTableMessage(self,delmsg,new,current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = Grid.GridTableMessage(self,addmsg,new-current)
                grid.ProcessTableMessage(msg)
                self.UpdateValues(grid)
        grid.EndBatch()

        # update the scrollbars and the displayed part of the grid
        dc = wx.MemoryDC()
        dc.SetFont(grid.editor.text_font)
        (width, height) = dc.GetTextExtent("M")
        grid.SetDefaultRowSize(height)
        grid.SetColMinimalAcceptableWidth(width)
        grid.SetRowMinimalAcceptableHeight(height + 1)

        for row in range(self._rows):
            # Can't share GridCellAttrs among columns; causes crash when
            # freeing them.  So, have to individually allocate the attrs for
            # each column
            cellattr = Grid.GridCellAttr()
            cellattr.SetFont(grid.editor.text_font)
            cellattr.SetBackgroundColour("white")
            renderer = FontGridRenderer(self, grid.editor)
            cellattr.SetRenderer(renderer)
            log.debug("hexcol %d width=%d" % (col,width))
            grid.SetRowMinimalHeight(col, height)
            grid.SetRowSize(row, (height * 2) + 4)
            grid.SetRowAttr(row, cellattr)

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
        
        label_font = grid.editor.text_font.Bold()
        grid.SetLabelFont(label_font)
        dc.SetFont(label_font)
        (width, height) = dc.GetTextExtent("M")
        grid.HideColLabels()
        text = self.GetRowLabelValue(self._rows - 1)
        grid.SetRowLabelSize(width * len(text) + 4)
        
        grid.AdjustScrollbars()
        grid.ForceRefresh()

    def UpdateValues(self, grid):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = Grid.GridTableMessage(self, Grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)


class FontGrid(Grid.Grid):
    """
    View for editing in hexidecimal notation.
    """

    def __init__(self, parent, task, table, **kwargs):
        """Create the HexEdit viewer
        """
        Grid.Grid.__init__(self, parent, -1, **kwargs)
        self.task = task
        self.editor = None
        if table is None:
            table = FontGridTable()
        self.table = table

        # The second parameter means that the grid is to take
        # ownership of the table and will destroy it when done.
        # Otherwise you would need to keep a reference to it and call
        # its Destroy method later.
        self.SetTable(self.table, True)
        self.SetMargins(0,0)
        self.SetColMinimalAcceptableWidth(10)
        self.EnableDragGridSize(False)
        self.DisableDragRowSize()

        self.RegisterDataType(Grid.GRID_VALUE_STRING, None, None)

        self.allow_range_select = True
        self.updateUICallback = None
        self.Bind(Grid.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftDown)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(Grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightDown)
#        self.Bind(Grid.EVT_GRID_SELECT_CELL, self.OnSelectCell)
#        self.Bind(Grid.EVT_GRID_RANGE_SELECT, self.OnSelectRange)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Show(True)

    def OnRightDown(self, evt):
        log.debug(self.GetSelectedRows())
        actions = self.get_popup_actions(r, c)
        if actions:
            self.editor.popup_context_menu_from_actions(self, actions)
    
    def get_popup_actions(self, r, c):
        return []

    def OnLeftDown(self, evt):
        c, r = (evt.GetCol(), evt.GetRow())
        self.ClearSelection()
        e = self.editor
        e.anchor_initial_start_index, e.anchor_initial_end_index = self.table.get_index_range(r, c)
        e.anchor_start_index, e.anchor_end_index = e.anchor_initial_start_index, e.anchor_initial_end_index
        evt.Skip()
        self.SetGridCursor(r, c)
        wx.CallAfter(self.ForceRefresh)
        wx.CallAfter(self.task.active_editor.index_clicked, e.anchor_start_index, 0, self)
 
    def on_motion(self, evt):
        e = self.editor
        if evt.LeftIsDown():
            x, y = evt.GetPosition()
            x, y = self.CalcUnscrolledPosition(x, y)
            r, c = self.XYToCell(x, y)
            index1, index2 = self.table.get_index_range(r, c)
            update = False
            if e.anchor_start_index <= index1:
                if index2 != e.anchor_end_index:
                    e.anchor_start_index = e.anchor_initial_start_index
                    e.anchor_end_index = index2
                    update = True
            else:
                if index1 != e.anchor_end_index:
                    e.anchor_start_index = e.anchor_initial_end_index
                    e.anchor_end_index = index1
                    update = True
            if update:
                self.SetGridCursor(r, c)
                wx.CallAfter(self.ForceRefresh)
                wx.CallAfter(self.task.active_editor.index_clicked, e.anchor_end_index, 0, self)
        evt.Skip()

    def OnSelectCell(self, evt):
        log.debug("cell selected r=%d c=%d" % (evt.GetCol(), evt.GetRow()))
        evt.Skip()

    def OnKeyDown(self, evt):
        log.debug("evt=%s" % evt)
        key = evt.GetKeyCode()
        moved = False
        r, c = self.GetGridCursorRow(), self.GetGridCursorCol()
        if key == wx.WXK_RETURN or key == wx.WXK_TAB:
            if evt.ControlDown():   # the edit control needs this key
                evt.Skip()
            else:
                self.DisableCellEditControl()
                if evt.ShiftDown():
                    (r, c) = self.table.getPrevCursorPosition(r, c)
                else:
                    (r, c) = self.table.getNextCursorPosition(r, c)
                moved = True
        elif key == wx.WXK_RIGHT:
            r, c = self.table.getNextCursorPosition(r, c)
            moved = True
        elif key == wx.WXK_LEFT:
            r, c = self.table.getPrevCursorPosition(r, c)
            moved = True
        elif key == wx.WXK_UP:
            r = 0 if r <= 1 else r - 1
            moved = True
        elif key == wx.WXK_DOWN:
            n = self.GetNumberRows()
            r = n - 1 if r >= n - 1 else r + 1
            moved = True
        else:
            evt.Skip()
        
        if moved:
            self.SetGridCursor(r, c)
            self.MakeCellVisible(r, c)
            index1, index2 = self.table.get_index_range(r, c)
            wx.CallAfter(self.task.active_editor.index_clicked, index1, 0, self)

    def abortEdit(self):
        self.DisableCellEditControl()

    def goto_index(self, index):
        row, col = self.table.get_row_col(index)
        self.SetGridCursor(row, col)
        self.MakeCellVisible(row,col)

    def select_index(self, cursor):
        self.ClearSelection()
        self.goto_index(cursor)
        self.ForceRefresh()
    
    def change_value(self, row, col, text):
        """Called after editor has provided a new value for a cell.
        
        Can use this to override the default handler.  Return True if the grid
        should be updated, or False if the value is invalid or the grid will
        be updated some other way.
        """
        self.table.SetValue(row, col, text) # update the table
        return True


class TileMapControl(FontGrid):
    """
    View for editing in hexidecimal notation.
    """

    def __init__(self, parent, task, **kwargs):
        """Create the HexEdit viewer
        """
        table = FontGridTable()
        FontGrid.__init__(self, parent, task, table, **kwargs)

    def recalc_view(self):
        editor = self.task.active_editor
        if editor is not None:
            self.editor = editor
            self.table.ResetView(self, editor)
            self.table.UpdateValues(self)
    
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
                cmd = ChangeByteCommand(self.table.segment, start, end, val)
                self.task.active_editor.process_command(cmd)
        except ValueError:
            pass
        return False
    
    def get_popup_actions(self, r, c):
        return [CutAction, CopyAction, PasteAction, None, SelectAllAction]
