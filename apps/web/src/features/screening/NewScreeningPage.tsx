import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as zod from "zod";
import { UploadCloud, FileText, X, AlertCircle } from "lucide-react";
import { Button } from "../../components/ui/Button";
import { api } from "../../services/api";
import { useScreeningStore } from "../../store/screeningStore";
import { motion, AnimatePresence } from "framer-motion";

const formSchema = zod.object({
  role_title: zod.string().min(1, "Role title is required"),
  job_description: zod.string().min(10, "Job description must be at least 10 characters"),
});

type FormDataFields = zod.infer<typeof formSchema>;

export const NewScreeningPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [fileError, setFileError] = useState<string | null>(null);
  const setActiveRun = useScreeningStore((s) => s.setActiveRun);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormDataFields>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      role_title: "",
      job_description: "",
    },
  });

  const mutation = useMutation({
    mutationFn: api.screenResumes,
    onSuccess: (data: any) => {
      setActiveRun(data);
      navigate(`/screen/${data.run_id}/review`);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files).filter(
        (f) => f.name.endsWith(".txt") || f.name.endsWith(".pdf") || f.name.endsWith(".docx")
      );
      if (selected.length === 0) {
        setFileError("Only .txt, .pdf, and .docx files are supported.");
        return;
      }
      setFileError(null);
      setFiles((prev) => [...prev, ...selected]);
    }
  };

  const removeFile = (idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const dropped = Array.from(e.dataTransfer.files).filter(
        (f) => f.name.endsWith(".txt") || f.name.endsWith(".pdf") || f.name.endsWith(".docx")
      );
      if (dropped.length === 0) {
        setFileError("Only .txt, .pdf, and .docx files are supported.");
        return;
      }
      setFileError(null);
      setFiles((prev) => [...prev, ...dropped]);
    }
  };

  const onSubmit = (data: FormDataFields) => {
    if (files.length === 0) {
      setFileError("Please upload at least one resume file.");
      return;
    }
    setFileError(null);

    const formData = new FormData();
    formData.append("role_title", data.role_title);
    formData.append("job_description", data.job_description);
    files.forEach((file) => {
      formData.append("resumes", file);
    });

    // Move to processing view
    navigate("/screen/processing");
    
    // Trigger mutation
    mutation.mutate(formData);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="p-10 max-w-3xl w-full mx-auto space-y-8"
    >
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
          Create Screening Campaign
        </h1>
        <p className="text-zinc-500 text-sm mt-1">
          Provide role parameters and upload target resumes to begin the candidate screening.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Role Title */}
        <div className="space-y-2">
          <label className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold">
            Role Title
          </label>
          <input
            {...register("role_title")}
            type="text"
            placeholder="e.g. Senior Machine Learning Engineer"
            className="w-full px-4 py-2.5 rounded-lg border border-zinc-200 focus:outline-none focus:ring-2 focus:ring-zinc-500 text-sm bg-white"
          />
          {errors.role_title && (
            <p className="text-red-500 text-xs mt-1">{errors.role_title.message}</p>
          )}
        </div>

        {/* Job Description */}
        <div className="space-y-2">
          <label className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold">
            Job Description Requirements
          </label>
          <textarea
            {...register("job_description")}
            rows={6}
            placeholder="Outline required experience, degree levels, and technical skill keywords..."
            className="w-full px-4 py-2.5 rounded-lg border border-zinc-200 focus:outline-none focus:ring-2 focus:ring-zinc-500 text-sm bg-white font-sans resize-y"
          />
          {errors.job_description && (
            <p className="text-red-500 text-xs mt-1">{errors.job_description.message}</p>
          )}
        </div>

        {/* Resumes Drag & Drop */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <label className="text-xs font-mono uppercase tracking-wider text-zinc-400 font-bold">
              Resumes (.txt, .pdf, .docx)
            </label>
            {files.length > 0 && (
              <span className="text-xs font-semibold text-zinc-500 bg-zinc-100 px-2 py-0.5 rounded-full font-mono">
                {files.length} {files.length === 1 ? "resume" : "resumes"} staged
              </span>
            )}
          </div>
          
          <div
            onDragOver={onDragOver}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-zinc-200 hover:border-zinc-300 rounded-xl p-8 text-center cursor-pointer transition-colors bg-zinc-50/20 group flex flex-col items-center justify-center"
          >
            <input
              type="file"
              multiple
              accept=".txt,.pdf,.docx"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
            />
            <UploadCloud className="w-8 h-8 text-zinc-400 group-hover:text-zinc-600 transition-colors mb-3 stroke-[1.5]" />
            <p className="text-sm font-medium text-zinc-700">
              Drag & drop resumes here, or <span className="underline">browse files</span>
            </p>
            <p className="text-xs text-zinc-400 mt-1">Supports PDF, DOCX, and Plain Text</p>
          </div>

          {fileError && (
            <div className="flex items-center gap-2 text-red-600 text-xs mt-2 font-medium">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{fileError}</span>
            </div>
          )}

          {/* Files List Display */}
          <AnimatePresence>
            {files.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 border border-zinc-200 rounded-xl bg-white divide-y divide-zinc-100 max-h-60 overflow-y-auto"
              >
                {files.map((file, idx) => (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    key={`${file.name}-${idx}`}
                    className="flex items-center justify-between p-3 text-sm text-zinc-800"
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <FileText className="w-4 h-4 text-zinc-400 shrink-0" />
                      <span className="truncate">{file.name}</span>
                      <span className="text-[10px] text-zinc-400 font-mono">
                        ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(idx)}
                      className="text-zinc-400 hover:text-zinc-600 p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Submit */}
        <div className="pt-4 border-t border-zinc-100 flex justify-end">
          <Button type="submit" variant="primary" className="h-10 px-6 rounded-lg text-sm">
            Begin Screening →
          </Button>
        </div>
      </form>
    </motion.div>
  );
};
