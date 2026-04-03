"use client";

import { motion } from "framer-motion";
import { Facebook, Twitter, Instagram, Mail } from "lucide-react";
import Image from "next/image";

export default function TeamPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
      },
    },
    hover: {
      y: -10,
      transition: {
        duration: 0.3,
      },
    },
  };

  const teamMembers = [
    {
      name: "Mrs. Sindhu Acharya",
      role: "ASSISTANT PROFESSOR",
      department: "Department of Computer Science",
      description:
        "Assistant Professor, Department of Computer Science, who guided and supported the development of this project.",
      image: "/teacher-sindhu.jpeg",
      social: {
        facebook: "#",
        twitter: "#",
        instagram: "#",
      },
    },
    {
      name: "Student Name",
      role: "PROJECT DEVELOPER",
      department: "Computer Science Student",
      description:
        "Developer of this project..",
      image: null, // No image - will show placeholder
      social: {
        facebook: "#",
        twitter: "#",
        instagram: "#",
      },
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 relative overflow-hidden py-20">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="text-center mb-16"
        >
          <motion.h1
            variants={cardVariants}
            className="text-5xl md:text-6xl font-bold gradient-text mb-6"
          >
            Meet Our Team
          </motion.h1>
          <motion.p
            variants={cardVariants}
            className="text-lg text-gray-400 max-w-2xl mx-auto"
          >
            The dedicated individuals behind this project
          </motion.p>
        </motion.div>

        {/* Team Cards */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 max-w-5xl mx-auto"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              variants={cardVariants}
              whileHover="hover"
              className="glass-card rounded-3xl p-8 md:p-10 text-center group relative overflow-hidden"
            >
              {/* Gradient Overlay on Hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-pink-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              <div className="relative z-10">
                {/* Profile Image */}
                <motion.div
                  className="relative w-40 h-40 mx-auto mb-6"
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full opacity-20 group-hover:opacity-40 transition-opacity duration-300" />
                  {member.image ? (
                    <Image
                      src={member.image}
                      alt={member.name}
                      width={160}
                      height={160}
                      className="rounded-full object-cover w-full h-full border-4 border-white/10 shadow-xl"
                    />
                  ) : (
                    <div className="w-full h-full rounded-full border-4 border-white/10 bg-gradient-to-br from-purple-600/20 to-pink-600/20 flex items-center justify-center shadow-xl">
                      <div className="w-20 h-20 rounded-full bg-white/10 flex items-center justify-center">
                        <Mail className="w-10 h-10 text-purple-400" />
                      </div>
                    </div>
                  )}
                </motion.div>

                {/* Role */}
                <p className="text-xs uppercase tracking-wider text-gray-500 mb-2 font-semibold">
                  {member.role}
                </p>

                {/* Name */}
                <h2 className="text-2xl md:text-3xl font-bold gradient-text mb-2">
                  {member.name}
                </h2>

                {/* Department */}
                <p className="text-sm text-purple-400 mb-4 font-medium">
                  {member.department}
                </p>

                {/* Description */}
                <p className="text-gray-400 leading-relaxed mb-8 min-h-[60px]">
                  {member.description}
                </p>

                {/* Social Media Icons */}
                <div className="flex items-center justify-center gap-4">
                  <motion.a
                    href={member.social.facebook}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-purple-700 flex items-center justify-center hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Facebook className="w-5 h-5 text-white" />
                  </motion.a>

                  <motion.a
                    href={member.social.twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Twitter className="w-5 h-5 text-white" />
                  </motion.a>

                  <motion.a
                    href={member.social.instagram}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-12 h-12 rounded-full bg-gradient-to-br from-pink-600 to-pink-700 flex items-center justify-center hover:from-pink-700 hover:to-pink-800 transition-all shadow-lg"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Instagram className="w-5 h-5 text-white" />
                  </motion.a>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Note for updating student info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-12 text-center"
        >
          <p className="text-sm text-gray-500 italic">
            * Student information and photo will be updated soon
          </p>
        </motion.div>
      </div>
    </div>
  );
}
