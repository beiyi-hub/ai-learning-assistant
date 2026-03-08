import React, { useState } from 'react';
import { Box, Drawer, AppBar, Toolbar, Typography, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider, IconButton } from '@mui/material';
import { Menu as MenuIcon, Chat as ChatIcon, Book as BookIcon, Home as HomeIcon, Settings as SettingsIcon } from '@mui/icons-material';
import './App.css';

// 导入组件
import ProjectManager from './components/ProjectManager/ProjectManager';
import ChatInterface from './components/ChatInterface/ChatInterface';
import KnowledgeBase from './components/KnowledgeBase/KnowledgeBase';
import Settings from './components/Settings/Settings';

// 定义视图类型
const VIEW_TYPES = {
  PROJECTS: 'projects',
  CHAT: 'chat',
  KNOWLEDGE_BASE: 'knowledge_base',
  SETTINGS: 'settings'
};

function App() {
  const [selectedProject, setSelectedProject] = useState(null);
  const [activeView, setActiveView] = useState(VIEW_TYPES.PROJECTS);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // 处理项目选择
  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    // 切换到聊天视图
    setActiveView(VIEW_TYPES.CHAT);
  };

  // 处理视图切换
  const handleViewChange = (view) => {
    setActiveView(view);
    // 如果切换到项目视图，清除当前选择的项目
    if (view === VIEW_TYPES.PROJECTS) {
      setSelectedProject(null);
    }
  };

  // 切换抽屉状态
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  // 侧边栏导航项
  const navItems = [
    { text: '项目管理', icon: <HomeIcon />, view: VIEW_TYPES.PROJECTS },
    { text: '聊天界面', icon: <ChatIcon />, view: VIEW_TYPES.CHAT, disabled: !selectedProject },
    { text: '知识库', icon: <BookIcon />, view: VIEW_TYPES.KNOWLEDGE_BASE, disabled: !selectedProject },
    { text: '设置', icon: <SettingsIcon />, view: VIEW_TYPES.SETTINGS },
  ];

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* 应用栏 */}
      <AppBar position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={toggleDrawer}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Trae 学习助手
          </Typography>
        </Toolbar>
      </AppBar>

      {/* 侧边栏抽屉 */}
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={toggleDrawer}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
          },
        }}
      >
        <Box sx={{ pt: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h6" sx={{ pl: 2, mb: 2 }}>
            导航菜单
          </Typography>
          <Divider />
          <List>
            {navItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  onClick={() => {
                    handleViewChange(item.view);
                    toggleDrawer();
                  }}
                  disabled={item.disabled}
                  selected={activeView === item.view}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Divider sx={{ mt: 'auto' }} />
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Trae 学习助手 v1.0
            </Typography>
          </Box>
        </Box>
      </Drawer>

      {/* 主内容区域 */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          pt: 8, // 为应用栏留出空间
          height: '100vh',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* 根据当前视图渲染不同的组件 */}
        {activeView === VIEW_TYPES.PROJECTS && (
          <ProjectManager onSelectProject={handleProjectSelect} />
        )}
        {activeView === VIEW_TYPES.CHAT && (
          <ChatInterface selectedProject={selectedProject} />
        )}
        {activeView === VIEW_TYPES.KNOWLEDGE_BASE && (
          <KnowledgeBase selectedProject={selectedProject} />
        )}
        {activeView === VIEW_TYPES.SETTINGS && (
          <Settings />
        )}
      </Box>
    </Box>
  );
}

export default App;
